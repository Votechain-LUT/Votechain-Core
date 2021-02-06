import asyncio
import os
from hfc.fabric import Client
from hfc.fabric.transaction.tx_proposal_request import CC_TYPE_NODE


loop = asyncio.get_event_loop()
CHANNEL = os.environ.get("CHANNEL_NAME", "businesschannel")
CHAINCODE_PEER_PATH = "hyperledger/chaincode"


class VotechainNetworkClient():
    def __init__(self):
        self.cli = Client(net_profile="hyperledger-network.json")
        self.user_org1 = self.cli.get_user(org_name="org1.example.com", name="Admin")
        self.user_org2 = self.cli.get_user(org_name="org2.example.com", name="Admin")
        self.chaincode_peers = ['peer0.org1.example.com', 'peer1.org1.example.com']
        self.chaincode_version = "v0"

    def add_poll(self, poll_id):
        chaincode_name = str(poll_id)
        loop.run_until_complete(
            self.cli.chaincode_install(
                requestor=self.user_org1,
                peers=self.chaincode_peers,
                cc_path=CHAINCODE_PEER_PATH,
                cc_name=chaincode_name,
                cc_type=CC_TYPE_NODE,
                cc_version=self.chaincode_version
            )
        )
        loop.run_until_complete(
            self.cli.chaincode_instantiate(
               requestor=self.user_org1,
               channel_name=CHANNEL,
               peers=self.chaincode_peers,
               args=[],
               cc_name=chaincode_name,
               cc_version=self.chaincode_version,
               cc_type=CC_TYPE_NODE,
               wait_for_event=True # optional, for being sure chaincode is instantiated
            )
        )

    def add_candidates(self, poll_id, candidates):
        chaincode_name = str(poll_id)
        args = [str(candidate) for candidate in candidates]
        loop.run_until_complete(
            self.cli.chaincode_invoke(
               requestor=self.user_org1,
               channel_name=CHANNEL,
               peers=self.chaincode_peers,
               args=args,
               cc_name=chaincode_name,
               cc_version=self.chaincode_version,
               cc_type=CC_TYPE_NODE,
               wait_for_event=True # optional, for being sure chaincode is instantiated
            )
        )
