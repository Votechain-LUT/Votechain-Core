import asyncio
import os
from hfc.fabric import Client
from hfc.fabric.transaction.tx_proposal_request import CC_TYPE_NODE
from votechain.settings import INTEGRATE_BLOCKCHAIN

CHANNEL = "businesschannel"
CHAINCODE_PATH = os.environ.get("CHAINCODE_PATH", "hyperledger/chaincode")
GET_RESULTS = "GetResults"
GET_RESULT = "GetResult"
SEND_VOTE = "SendVote"
ADD_CANDIDATES = "AddCandidates"
DELETE_CANDIDATES = "DeleteCandidates"
VERIFY_VOTE = "VerifyVote"
CHAINCODE_PREFIX = os.environ.get("CHAINCODE_PREFIX", "Votechain-")


class VotechainNetworkClient():
    def __init__(self):
        if INTEGRATE_BLOCKCHAIN:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            self.cli = Client(net_profile="hyperledger-network.json")
            self.cli.new_channel(CHANNEL)
            self.user_org1 = self.cli.get_user(org_name="org1.example.com", name="Admin")
            self.user_org2 = self.cli.get_user(org_name="org2.example.com", name="Admin")
            self.chaincode_peers = ['peer0.org1.example.com', 'peer1.org1.example.com']
            self.chaincode_version = "v0"

    def _get_chaincode_name(self, poll_id):
        """ Returns chaincode name based on poll id and predefined prefix """
        return CHAINCODE_PREFIX + str(poll_id)

    def _invoke_chaincode(self, poll_id, method_name, params):
        """ Invokes a chaincode function and returns result string (JSON format) """
        if INTEGRATE_BLOCKCHAIN:
            try:
                chaincode_name = self._get_chaincode_name(poll_id)
                args = [method_name]
                for param in params:
                    args.append(str(param))
                return self.loop.run_until_complete(
                    self.cli.chaincode_invoke(
                        requestor=self.user_org1,
                        channel_name=CHANNEL,
                        peers=self.chaincode_peers,
                        args=args,
                        cc_name=chaincode_name,
                        cc_type=CC_TYPE_NODE,
                        wait_for_event=True
                    )
                )
            except Exception as ex:
                print(ex)
                raise ex
        return ""

    def add_poll(self, poll_id):
        """ Creates a poll as a new chaincode instance """
        if INTEGRATE_BLOCKCHAIN:
            try:
                chaincode_name = self._get_chaincode_name(poll_id)
                self.loop.run_until_complete(
                    self.cli.chaincode_install(
                        requestor=self.user_org1,
                        peers=self.chaincode_peers,
                        cc_path=CHAINCODE_PATH,
                        cc_name=chaincode_name,
                        cc_type=CC_TYPE_NODE,
                        cc_version=self.chaincode_version
                    )
                )
                return self.loop.run_until_complete(
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
            except Exception as ex:
                print(ex)
                raise ex
        return ""

    def add_candidates(self, poll_id, candidates):
        """ Adds candidates to a poll """
        return self._invoke_chaincode(poll_id, ADD_CANDIDATES, candidates)

    def delete_candidates(self, poll_id, candidates):
        """ Deletes candidates from a poll """
        return self._invoke_chaincode(poll_id, DELETE_CANDIDATES, candidates)

    def get_results(self, poll_id):
        """ Returns poll results for all candidates """
        return self._invoke_chaincode(poll_id, GET_RESULTS, [])

    def get_results_for_candidate(self, poll_id, candidate):
        """ Returns poll results for one candidate """
        return self._invoke_chaincode(poll_id, GET_RESULT, [candidate])

    def cast_vote(self, poll_id, candidate):
        """ Casts a vote on given candidate """
        return self._invoke_chaincode(poll_id, SEND_VOTE, [candidate])

    def verify_vote(self, poll_id, token):
        """ Returns candidate who was casted in a given transaction """
        return self._invoke_chaincode(poll_id, VERIFY_VOTE, [token])
