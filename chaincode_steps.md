# steps to install chaincode in debug

``` bash
terminal (#1)
clone fabric-samples tag v1.4.6
cd fabric-samples/chaincode-docker-devmode
export HLF_VERSION=1.4.6
docker-compose -f docker-compose-simple.yaml up
docker exec -it chaincode bash
npm start -- --peer.address peer:7052 --chaincode-id-name "votechain:v0"
```

new terminal (#2)

``` bash
docker exec -it cli bash
peer chaincode install -p chaincode/votechain -n votechain -v v0 -l node

new terminal (#3)

``` bash
docker tag hyperledger/fabric-ccenv:1.4.6 hyperledger/fabric-ccenv:latest
```

back to terminal #2

``` bash
peer chaincode instantiate -n votechain -v v0 -c '{"Args":["init"]}' -o orderer:7050 -C "myc"
```

## upgrading (run on peer)

``` bash
peer chaincode install -p chaincode/votechain -n votechain2 -v v1 -l node
peer chaincode instantiate -n votechain2 -v v1 -c '{"Args":["init", "A", "B"]}' -o orderer:7050 -C "myc"
```

## example workflow

``` bash
peer chaincode invoke -C "myc" -n "votechain" -c '{"args": ["AddCandidates", "A", "B"]}'
peer chaincode invoke -C "myc" -n "votechain" -c '{"args": ["GetResults"]}'
peer chaincode invoke -C "myc" -n "votechain" -c '{"args": ["GetResult", "A"]}'
peer chaincode invoke -C "myc" -n "votechain" -c '{"args": ["SendVote", "A"]}'
peer chaincode invoke -C "myc" -n "votechain" -c '{"args": ["SendVote", "A"]}'
peer chaincode invoke -C "myc" -n "votechain" -c '{"args": ["SendVote", "A"]}'
peer chaincode invoke -C "myc" -n "votechain" -c '{"args": ["SendVote", "B"]}'
peer chaincode invoke -C "myc" -n "votechain" -c '{"args": ["GetResults"]}'
peer chaincode invoke -C "myc" -n "votechain" -c '{"args": ["GetResult", "A"]}'
peer chaincode invoke -C "myc" -n "votechain" -c '{"args": ["VerifyVote", "50c32d8517da99e143b7dab98b51def35051f56ae82e1f2ae20258b509ac5ded"]}'
```
