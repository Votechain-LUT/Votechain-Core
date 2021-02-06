import os
import sys
from hfc.fabric import Client



def main(channel_config_path):
    """
    Creates a channel in the network and joins all peers into that channel
    This script should be run once per network deployment
    """
    channel = os.environ.get("CHANNEL_NAME", "businesschannel")
    cli = Client(net_profile="hyperledger-network.json")
    user_org1 = cli.get_user(org_name="org1.example.com", name="Admin")
    user_org2 = cli.get_user(org_name="org2.example.com", name="Admin")
    cli.channel_create(
        orderer='orderer.example.com',
        channel_name=channel,
        requestor=user_org1,
        config_yaml=channel_config_path,
        channel_profile='TwoOrgsChannel'
    )
    cli.channel_join(
        orderer='orderer.example.com',
        channel_name=channel,
        requestor=user_org1,
        peers=['peer0.org1.example.com',
            'peer1.org1.example.com'],
    )
    cli.channel_join(
        orderer='orderer.example.com',
        channel_name=channel,
        requestor=user_org2,
        peers=['peer0.org2.example.com',
            'peer1.org2.example.com'],
    )


if __name__ == "__main__":
    channel_path = sys.argv[1] if len(sys.argv) > 1 else "hyperledger/channel"
    main(channel_path)
