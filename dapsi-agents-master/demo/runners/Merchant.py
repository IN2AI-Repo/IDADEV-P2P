import random
import asyncio
import json
import logging
import os
import sys
import csv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # noqa

from datetime import date
from uuid import uuid4
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

TAILS_FILE_COUNT = int(os.getenv("TAILS_FILE_COUNT", 100))

LOGGER = logging.getLogger(__name__)


class MerchantAgent(DemoAgent):
    def __init__(self,
                 http_port: int,
                 admin_port: int,
                 **kwargs):
        super().__init__(
            "Merchant Agent",
            http_port,
            admin_port,
            prefix="Merchant",
            extra_args=["--auto-accept-invites", "--auto-accept-requests"],
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
            if message["state"] == "active" and not self._connection_ready.done():
                self.log("Connected")
                self._connection_ready.set_result(True)

    async def handle_present_proof(self, message):
        state = message["state"]
        lst = []

        presentation_exchange_id = message["presentation_exchange_id"]
        self.log("Presentation (" + presentation_exchange_id + ") state =", state)

        if state == "presentation_received":
            log_status("Receive and verify proof provided by user")

            proof = await self.admin_POST(
                f"/present-proof/records/{presentation_exchange_id}/verify-presentation"
            )
            self.log("Proof verification result: " + proof["verified"])

            pres_req = message["presentation_request"]
            pres = message["presentation"]
            
            is_proof_of_personaldata = (
                pres_req["name"] == "Proof of Personal Data"
            )

            if is_proof_of_personaldata:

                if (proof["verified"] == "false"):
                    await self.admin_POST(f"/connections/{self.connection_id}/send-message", {
                        "content": "Invalid proof presented to " + self.ident}
                    )
                    pass

                elif (proof["verified"] == "true"):
                    
                    log_status("Check proof claims")

                    self.log("----------------------------------------------------------------------------------")
                    self.log("Proof claims:")
                    for (referent, attr_spec) in pres_req["requested_attributes"].items():
                        self.log(
                            f"    {attr_spec['name']}: "
                            f"{pres['requested_proof']['revealed_attrs'][referent]['raw']}"
                        )
                        lst.append(pres['requested_proof']['revealed_attrs'][referent]['raw'])
                        
                    with open('./demo/files/personal_data.txt', newline='') as csv_file:
                        csv_reader = csv.DictReader(csv_file)
                        line_count = 0
                        for row in csv_reader:
                            self.log("----------------------------------------------------------------------------------")
                            if((row["service"] == lst[0]) and row["checksum"] == lst[1]):
                                self.log("Claims verification completed successfully")
                                self.log("Sending voucher to user")
                                await self.admin_POST(f"/connections/{self.connection_id}/send-message", {
                                    "content": "Voucher received from " + self.ident + " : SJR7 - 93B5 - MN0u - 7EJ3"}
                                )
                            else:
                                self.log("Data verification failed")
                            line_count += 1

                    self.log("----------------------------------------------------------------------------------")

                    self.log("Schema ID and Credential Definition ID of presented claims:")
                    for id_spec in pres["identifiers"]:
                        self.log(f"    schema_id:   {id_spec['schema_id']}")
                        self.log(f"    cred_def_id: {id_spec['cred_def_id']}")
                    self.log("----------------------------------------------------------------------------------")

            else:
                self.log("Received ", message["presentation_request"]["name"])
                pass

            del lst

    async def handle_basicmessages(self, message):
        self.log("Received message:", message["content"])

async def main(start_port: int, show_timing: bool = True):

    genesis = await default_genesis_txns()
    if not genesis:
        print("Error retrieving ledger genesis transactions")
        sys.exit(1)

    agent = None

    try:
        log_status("Provision an agent and wallet")
        agent = MerchantAgent(
            start_port,
            start_port + 1,
            genesis_data=genesis
            )

        await agent.listen_webhooks(start_port + 2)

        await agent.register_did()

        await agent.start_process()
        
        agent.log("Admin URL is at:", agent.admin_url)
        agent.log("Endpoint URL is at:", agent.endpoint)

        log_status("-----------------------------------------------------------------------------------------------")
        log_status("Generate invitation and show details")
        connection = await agent.admin_POST("/connections/create-invitation")
        agent.log("Generate invitation")

        agent.connection_id = connection["connection_id"]
        log_json(connection)

        log_status("Use the invitation to connnect with other agents")
        log_msg(json.dumps(connection["invitation"]), label="Invitation:", color=None)
        log_status("-----------------------------------------------------------------------------------------------")

        agent.log("Waiting for connection...")
        await agent.detect_connection()

        async for option in prompt_loop(
            "-----------------------------------------------------------------------------------------------\n"
            "(1) Send Proof Request\n" +
            "(2) Send Message\n" +
            "(X) Exit\n" +
            "Select an action: "
        ):
            option = option.strip()
            if option in "xX":
                break

            elif option == "1":
                log_status("Request proof of personal data from user")
                agent.log("Generate proof request")

                indy_proof_request = {
                    "name": "Proof of Personal Data",
                    "version": "1.0",
                    "requested_attributes":
                    {
                        "0_service_uuid": {
                            "name": "service",  
                            "restrictions": [
                                {
                                    "cred_def_id": "WjF5TKdbmzNu69cVm5fBGA:3:CL:390:default",
                                    "schema_name": "personal_data_schema",
                                    "schema_version": "80.55.95"
                                },
                            ]
                        },
                        
                        "0_checksum_uuid": {
                            "name": "checksum",
                            "restrictions": [
                                {
                                    "cred_def_id": "WjF5TKdbmzNu69cVm5fBGA:3:CL:390:default",
                                    "schema_name": "personal_data_schema",
                                    "schema_version": "80.55.95"
                                },
                            ]
                        }
                    },
                    "requested_predicates": {},
                }

                proof_request_web_request = {
                    "connection_id": agent.connection_id,
                    "proof_request": indy_proof_request,
                }

                log_json(proof_request_web_request)
                agent.log("Sending proof request")

                await agent.admin_POST(
                    "/present-proof/send-request", proof_request_web_request
                )

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

    parser = argparse.ArgumentParser(description="Runs an Merchant demo agent.")
    parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=8060,
        metavar=("<port>"),
        help="Choose the starting port number to listen on",
    )
    parser.add_argument(
        "--timing", action="store_true", help="Enable timing information"
    )
    args = parser.parse_args()

    require_indy()

    try:
        asyncio.get_event_loop().run_until_complete(main(args.port, args.timing))
    except KeyboardInterrupt:
        os._exit(1)
