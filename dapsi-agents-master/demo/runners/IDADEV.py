import asyncio
import json
import logging
import os
import random
import sys
import time

import qrcode

from aiohttp import ClientError

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # noqa

from runners.support.agent import DemoAgent, default_genesis_txns
from runners.support.utils import (
    log_json,
    log_msg,
    log_status,
    log_timer,
    prompt,
    prompt_loop,
    require_indy,
)

CRED_PREVIEW_TYPE = "https://didcomm.org/issue-credential/1.0/credential-preview"

LOGGER = logging.getLogger(__name__)

TAILS_FILE_COUNT = int(os.getenv("TAILS_FILE_COUNT", 100))


class IDADEVAgent(DemoAgent):
    def __init__(
        self,
        http_port: int,
        admin_port: int,
        no_auto: bool = False,
        tails_server_base_url: str = None,
        **kwargs,
    ):
        super().__init__(
            "IDADEV Agent",
            http_port,
            admin_port,
            prefix="IDADEV",
            tails_server_base_url=tails_server_base_url,
            extra_args=[]
            if no_auto
            else ["--auto-accept-invites", "--auto-accept-requests"],
            **kwargs,
        )
        self.connection_id = None
        self._connection_ready = asyncio.Future()
        self.cred_state = {}
        self.cred_attrs = {}

    async def detect_connection(self):
        await self._connection_ready

    @property
    def connection_ready(self):
        return self._connection_ready.done() and self._connection_ready.result()

    async def handle_connections(self, message):
        if message["connection_id"] == self.connection_id:
            if message["state"] in ["active", "response"]:
                self.log("Connected")
                self._connection_ready.set_result(True)
                if not self._connection_ready.done():
                    self._connection_ready.set_result(True)

    async def handle_issue_credential(self, message):
        state = message["state"]
        credential_exchange_id = message["credential_exchange_id"]
        prev_state = self.cred_state.get(credential_exchange_id)
        if prev_state == state:
            return
        self.cred_state[credential_exchange_id] = state

        self.log("Credential (" + credential_exchange_id + ") state =", state)

        if state == "request_received":
            log_status("Issue credential to user")

            cred_attrs = self.cred_attrs[message["credential_definition_id"]]
            cred_preview = {
                "@type": CRED_PREVIEW_TYPE,
                "attributes": [
                    {"name": n, "value": v} for (n, v) in cred_attrs.items()
                ],
            }
            try:
                cred_ex_rec = await self.admin_POST(
                    f"/issue-credential/records/{credential_exchange_id}/issue",
                    {
                        "comment": (
                            f"Issuing credential, exchange {credential_exchange_id}"
                        ),
                        "credential_preview": cred_preview,
                    },
                )
                rev_reg_id = cred_ex_rec.get("revoc_reg_id")
                cred_rev_id = cred_ex_rec.get("revocation_id")
                if rev_reg_id:
                    self.log(f"Revocation registry ID: {rev_reg_id}")
                if cred_rev_id:
                    self.log(f"Credential revocation ID: {cred_rev_id}")
            except ClientError:
                pass

    async def handle_present_proof(self, message):
        state = message["state"]

        presentation_exchange_id = message["presentation_exchange_id"]
        self.log(
            "Presentation: state =",
            state,
            ", presentation_exchange_id =",
            presentation_exchange_id,
        )

        if state == "presentation_received":
            log_status("#27 Process the proof provided by X")
            log_status("#28 Check if proof is valid")
            proof = await self.admin_POST(
                f"/present-proof/records/{presentation_exchange_id}/verify-presentation"
            )
            self.log("Proof =", proof["verified"])

    async def handle_basicmessages(self, message):
        self.log("Received message:", message["content"])


async def main(
    start_port: int,
    no_auto: bool = False,
    revocation: bool = False,
    tails_server_base_url: str = None,
    show_timing: bool = False,
):

    genesis = await default_genesis_txns()
    if not genesis:
        print("Error retrieving ledger genesis transactions")
        sys.exit(1)

    agent = None

    try:
        log_status("Provision an agent and wallet")
        agent = IDADEVAgent(
            start_port,
            start_port + 1,
            genesis_data=genesis,
            no_auto=no_auto,
            tails_server_base_url=tails_server_base_url,
        )
        await agent.listen_webhooks(start_port + 2)
        await agent.register_did()

        await agent.start_process()
        agent.log("Admin URL is at:", agent.admin_url)
        agent.log("Endpoint URL is at:", agent.endpoint)

        log_status("Register schema and credential definition on the ledger")

        version = format(
            "%d.%d.%d"
            % (
                random.randint(1, 101),
                random.randint(1, 101),
                random.randint(1, 101),
            )
        )
        (
            _,  # schema id
            credential_definition_id,
        ) = await agent.register_schema_and_creddef(
            "personal_data_schema",
            version,
            ["name", "date", "service", "checksum", "timestamp"],
            support_revocation=revocation,
            revocation_registry_size=TAILS_FILE_COUNT if revocation else None,
        )

        log_status("-----------------------------------------------------------------------------------------------")
        log_status("Generate invitation and show details")
        connection = await agent.admin_POST("/connections/create-invitation")
        agent.log("Generate invitation")

        agent.connection_id = connection["connection_id"]
        log_json(connection)

        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L)
        qr.add_data(connection["invitation_url"])
        
        log_status("Use the invitation to connnect with other agents")
        log_msg(json.dumps(connection["invitation"]), label="Invitation:", color=None)
        log_status("-----------------------------------------------------------------------------------------------")

        #qr.print_ascii(invert=True)

        agent.log("Waiting for connection...")
        await agent.detect_connection()

        exchange_tracing = False
        options = (
            "-----------------------------------------------------------------------------------------------\n"
            "(1) Issue Credential\n"
            "(2) Send Message\n"
            "(T) Toggle tracing on credential/proof exchange\n"
            "(X) Exit\n"
            "Select an action: "
        )

        async for option in prompt_loop(options):
            if option is not None:
                option = option.strip()

            if option is None or option in "xX":
                break

            elif option in "tT":
                exchange_tracing = not exchange_tracing
                log_msg(
                    ">>> Credential/Proof Exchange Tracing is {}".format(
                        "ON" if exchange_tracing else "OFF"
                    )
                )
            elif option == "1":
                log_status("Issue credential offer to user")

                agent.cred_attrs[credential_definition_id] = {
                    "name": "Alice Smith",
                    "date": "2021-01-12",
                    "service": "Amazon",
                    "checksum": "84a3f860d54f3f5f65e91df081c8d776e8bcfb5fbc234afce2f0d7e9d26e160d",
                    "timestamp": str(int(time.time())),
                }

                cred_preview = {
                    "@type": CRED_PREVIEW_TYPE,
                    "attributes": [
                        {"name": n, "value": v}
                        for (n, v) in agent.cred_attrs[credential_definition_id].items()
                    ],
                }
                offer_request = {
                    "connection_id": agent.connection_id,
                    "cred_def_id": credential_definition_id,
                    "comment": f"Offer on cred def id {credential_definition_id}",
                    "auto_remove": False,
                    "credential_preview": cred_preview,
                    "trace": exchange_tracing,
                }
                await agent.admin_POST("/issue-credential/send-offer", offer_request)

            elif option == "2":
                msg = await prompt("Enter message: ")
                await agent.admin_POST(
                    f"/connections/{agent.connection_id}/send-message", {"content": msg}
                )

        if show_timing:
            timing = await agent.fetch_timing()
            if timing:
                for line in agent.format_timing(timing):
                    log_msg(line)

    finally:
        terminated = True
        try:
            if agent:
                await agent.terminate()
        except Exception:
            LOGGER.exception("Error terminating agent:")
            terminated = False

    await asyncio.sleep(0.1)

    if not terminated:
        os._exit(1)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Runs a IDADEV demo agent.")
    parser.add_argument("--no-auto", action="store_true", help="Disable auto issuance")
    parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=8020,
        metavar=("<port>"),
        help="Choose the starting port number to listen on",
    )
    parser.add_argument(
        "--revocation", action="store_true", help="Enable credential revocation"
    )

    parser.add_argument(
        "--tails-server-base-url",
        type=str,
        metavar=("<tails-server-base-url>"),
        help="Tals server base url",
    )

    parser.add_argument(
        "--timing", action="store_true", help="Enable timing information"
    )
    args = parser.parse_args()

    ENABLE_PYDEVD_PYCHARM = os.getenv("ENABLE_PYDEVD_PYCHARM", "").lower()
    ENABLE_PYDEVD_PYCHARM = ENABLE_PYDEVD_PYCHARM and ENABLE_PYDEVD_PYCHARM not in (
        "false",
        "0",
    )
    PYDEVD_PYCHARM_HOST = os.getenv("PYDEVD_PYCHARM_HOST", "localhost")
    PYDEVD_PYCHARM_CONTROLLER_PORT = int(
        os.getenv("PYDEVD_PYCHARM_CONTROLLER_PORT", 5001)
    )

    if ENABLE_PYDEVD_PYCHARM:
        try:
            import pydevd_pycharm

            print(
                "IDADEV remote debugging to "
                f"{PYDEVD_PYCHARM_HOST}:{PYDEVD_PYCHARM_CONTROLLER_PORT}"
            )
            pydevd_pycharm.settrace(
                host=PYDEVD_PYCHARM_HOST,
                port=PYDEVD_PYCHARM_CONTROLLER_PORT,
                stdoutToServer=True,
                stderrToServer=True,
                suspend=False,
            )
        except ImportError:
            print("pydevd_pycharm library was not found")

    require_indy()

    tails_server_base_url = args.tails_server_base_url or os.getenv("PUBLIC_TAILS_URL")

    if args.revocation and not tails_server_base_url:
        raise Exception(
            "If revocation is enabled, --tails-server-base-url must be provided"
        )

    try:
        asyncio.get_event_loop().run_until_complete(
            main(
                args.port,
                args.no_auto,
                args.revocation,
                tails_server_base_url,
                args.timing,
            )
        )
    except KeyboardInterrupt:
        os._exit(1)
