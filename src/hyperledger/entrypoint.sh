#!/bin/sh
sleep 7
docker network create hyperledger_dind_network
docker-compose up
