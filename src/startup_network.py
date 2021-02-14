import asyncio
import json
import os
import shutil
import sys
sys.path.append('..')
from hfc.fabric import Client


PEER_PREFIX = os.environ.get("PEER_PREFIX", "PEER_")
ORDERER_PREFIX = os.environ.get("ORDERER_PREFIX", "ORDERER_")
NETWORK_FILEPATH = "hyperledger-network.json"


def get_urls_from_env(env_prefix):
    """ reads all peer urls saved in environment variables prefixed with PEER_PREFIX setting """
    urls = {}
    for key in os.environ:
        if key.startswith(env_prefix):
            suffix_index = key.rindex("_")
            name = key[len(env_prefix):suffix_index].lower().replace("__", ".")
            suffix = key[suffix_index + 1:]
            if name in urls:
                urls[name][suffix] = os.environ[key]
            else:
                urls[name] = {suffix: os.environ[key]}
    return urls


def update_network_settings(network_config_path):
    """
    Changes peers and orgs urls based on environment variables
    """
    custom_peers = get_urls_from_env(PEER_PREFIX)
    custom_orderers = get_urls_from_env(ORDERER_PREFIX)
    with open(network_config_path, "r") as network_file:
        network = json.load(network_file)
        for key in network["peers"]:
            if key.lower() in custom_peers:
                for endpoint_type in custom_peers[key]:
                    url = custom_peers[key.lower()][endpoint_type]
                    if endpoint_type == "URL":
                        network["peers"][key]["url"] = url
                    elif endpoint_type == "EVENT":
                        network["peers"][key]["eventUrl"] = url
                    elif endpoint_type == "GRPC":
                        network["peers"][key]["grpcOptions"]["grpc.ssl_target_name_override"] = url
        for key in network["orderers"]:
            if key.lower() in custom_orderers:
                for endpoint_type in custom_orderers[key]:
                    url = custom_orderers[key.lower()][endpoint_type]
                    if endpoint_type == "URL":
                        network["orderers"][key]["url"] = url
                    elif endpoint_type == "GRPC":
                        network["orderers"][key]["grpcOptions"]["grpc.ssl_target_name_override"] = url
        with open(network_config_path + "_2", "w+") as output_file:
            json.dump(network, output_file)
    shutil.move(network_config_path + "_2", network_config_path)


def main(channel_config_path, network_config_path):
    """
    Creates a channel in the network and joins all peers into that channel
    This script should be run once per network deployment
    """
    channel = os.environ.get("CHANNEL_NAME", "businesschannel")
    loop = asyncio.get_event_loop()
    update_network_settings(network_config_path)
    cli = Client(net_profile=NETWORK_FILEPATH)
    user_org1 = cli.get_user(org_name="org1.example.com", name="Admin")
    user_org2 = cli.get_user(org_name="org2.example.com", name="Admin")
    loop.run_until_complete(
        cli.channel_create(
            orderer='orderer.example.com',
            channel_name=channel,
            requestor=user_org1,
            config_yaml=channel_config_path,
            channel_profile='TwoOrgsChannel'
        )
    )
    loop.run_until_complete(
        cli.channel_join(
            orderer='orderer.example.com',
            channel_name=channel,
            requestor=user_org1,
            peers=['peer0.org1.example.com',
                'peer1.org1.example.com'],
        )
    )
    loop.run_until_complete(
        cli.channel_join(
            orderer='orderer.example.com',
            channel_name=channel,
            requestor=user_org2,
            peers=['peer0.org2.example.com',
                'peer1.org2.example.com'],
        )
    )


if __name__ == "__main__":
    channel_path = sys.argv[1] if len(sys.argv) > 1 else "hyperledger/channel"
    network_path = sys.argv[2] if len(sys.argv) > 2 else NETWORK_FILEPATH
    main(channel_path, network_path)
