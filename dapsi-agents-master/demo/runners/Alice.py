import asyncio
import base64
import binascii
import json
import logging
import os
import sys
from urllib.parse import urlparse

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

LOGGER = logging.getLogger(__name__)


class AliceAgent(DemoAgent):
    def __init__(
        self, http_port: int, admin_port: int, no_auto: bool = False, **kwargs
    ):
        super().__init__(
            "Alice Agent",
            http_port,
            admin_port,
            prefix="Alice",
            extra_args=[]
            if no_auto
            else [
                "--auto-accept-invites",
                "--auto-accept-requests",
                "--auto-store-credential",
            ],
            seed=None,
            **kwargs,
        )
        self.connection_id = None
        self._connection_ready = asyncio.Future()
        self.cred_state = {}

    async def detect_connection(self):
        await self._connection_ready

    @property
    def connection_ready(self):
        return self._connection_ready.done() and self._connection_ready.result()

    async def handle_connections(self, message):
        if message["connection_id"] == self.connection_id:
            if message["state"] == "active" and not self._connection_ready.done():
                self.log("Connected")
                self._connection_ready.set_result(True)

    async def handle_issue_credential(self, message):
        state = message["state"]
        credential_exchange_id = message["credential_exchange_id"]
        prev_state = self.cred_state.get(credential_exchange_id)
        if prev_state == state:
            return  # ignore
        self.cred_state[credential_exchange_id] = state

        self.log("Credential (" + credential_exchange_id + ") state =", state)

        if state == "offer_received":
            log_status("Credential offer received. Send credential request")
            await self.admin_POST(
                f"/issue-credential/records/{credential_exchange_id}/send-request"
            )

        elif state == "credential_acked":
            cred_id = message["credential_id"]
            self.log(f"Stored credential {cred_id} in wallet")
            log_status(f"Stored credential in wallet")
            resp = await self.admin_GET(f"/credential/{cred_id}")
    
            log_status("-----------------------------------------------------------------------------------------------")
            log_status("Show credential details")

            log_json(resp)

            self.log("Credential ID: ", message["credential_id"])
            self.log("Credential definition ID: ", message["credential_definition_id"])
            self.log("Schema ID: ", message["schema_id"])

    async def handle_present_proof(self, message):
        state = message["state"]
        presentation_exchange_id = message["presentation_exchange_id"]
        presentation_request = message["presentation_request"]

        self.log("Presentation (" + presentation_exchange_id + ") state =", state)

        if state == "request_received":
            self.log("Query for credentials in the wallet that satisfy the proof request")

            credentials_by_reft = {}
            revealed = {}
            self_attested = {}
            predicates = {}

            # select credentials to provide for the proof
            credentials = await self.admin_GET(
                f"/present-proof/records/{presentation_exchange_id}/credentials"
            )
            if credentials:
                for row in sorted(
                    credentials,
                    key=lambda c: int(c["cred_info"]["attrs"]["timestamp"]),
                    reverse=True,
                ):
                    for referent in row["presentation_referents"]:
                        if referent not in credentials_by_reft:
                            credentials_by_reft[referent] = row

            for referent in presentation_request["requested_attributes"]:
                if referent in credentials_by_reft:
                    revealed[referent] = {
                        "cred_id": credentials_by_reft[referent]["cred_info"][
                            "referent"
                        ],
                        "revealed": True,
                    }
                else:
                    self_attested[referent] = "my self-attested value"

            for referent in presentation_request["requested_predicates"]:
                if referent in credentials_by_reft:
                    predicates[referent] = {
                        "cred_id": credentials_by_reft[referent]["cred_info"][
                            "referent"
                        ]
                    }

            self.log("Generate the proof")
            request = {
                "requested_predicates": predicates,
                "requested_attributes": revealed,
                "self_attested_attributes": self_attested,
            }

            log_status("Send the proof to Merchant")
            await self.admin_POST(
                (
                    "/present-proof/records/"
                    f"{presentation_exchange_id}/send-presentation"
                ),
                request,
            )

    async def handle_basicmessages(self, message):
        self.log("Received message:", message["content"])


async def input_invitation(agent):
    async for details in prompt_loop("Invite details: "):
        b64_invite = None
        try:
            url = urlparse(details)
            query = url.query
            if query and "c_i=" in query:
                pos = query.index("c_i=") + 4
                b64_invite = query[pos:]
            else:
                b64_invite = details
        except ValueError:
            b64_invite = details

        if b64_invite:
            try:
                padlen = 4 - len(b64_invite) % 4
                if padlen <= 2:
                    b64_invite += "=" * padlen
                invite_json = base64.urlsafe_b64decode(b64_invite)
                details = invite_json.decode("utf-8")
            except binascii.Error:
                pass
            except UnicodeDecodeError:
                pass

        if details:
            try:
                json.loads(details)
                break
            except json.JSONDecodeError as e:
                log_msg("Invalid invitation:", str(e))


    log_status("-----------------------------------------------------------------------------------------------")
    log_status("Receive invitation and show details")

    connection = await agent.admin_POST("/connections/receive-invitation", details)
    agent.connection_id = connection["connection_id"]
    log_json(connection)

    await agent.detect_connection()


async def main(start_port: int, no_auto: bool = False, show_timing: bool = False):

    genesis = await default_genesis_txns()
    if not genesis:
        print("Error retrieving ledger genesis transactions")
        sys.exit(1)

    agent = None

    try:
        log_status("Provision an agent and wallet")
        agent = AliceAgent(
            start_port,
            start_port + 1,
            genesis_data=genesis,
            no_auto=no_auto,
        )
        await agent.listen_webhooks(start_port + 2)

        await agent.start_process()

        agent.log("Admin URL is at:", agent.admin_url)
        agent.log("Endpoint URL is at:", agent.endpoint)

        log_status("-----------------------------------------------------------------------------------------------")
        log_status("Input IDADEV invitation details")

        await input_invitation(agent)

        async for option in prompt_loop(
            "------------------------------------------------------------------------------\n"
            "(1) Send Message\n" +
            "(2) Input New Invitation\n" +
            "(X) Exit\n" +
            "Select an action: "
        ):
            if option is not None:
                option = option.strip()

            if option is None or option in "xX":
                break

            elif option == "1":
                msg = await prompt("Enter message: ")
                if msg:
                    await agent.admin_POST(
                        f"/connections/{agent.connection_id}/send-message",
                        {"content": msg},
                    )
            elif option == "2":
                # handle new invitation
                log_status("Input new invitation details")
                await input_invitation(agent)

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

    parser = argparse.ArgumentParser(description="Runs an Alice demo agent.")
    parser.add_argument("--no-auto", action="store_true", help="Disable auto issuance")
    parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=8030,
        metavar=("<port>"),
        help="Choose the starting port number to listen on",
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
                f"Alice remote debugging to {PYDEVD_PYCHARM_HOST}:{PYDEVD_PYCHARM_CONTROLLER_PORT}"
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

    try:
        asyncio.get_event_loop().run_until_complete(
            main(args.port, args.no_auto, args.timing)
        )
    except KeyboardInterrupt:
        os._exit(1)
