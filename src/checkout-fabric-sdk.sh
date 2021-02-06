#!/bin/bash

if [ ! -d hfc ]
then
    git clone -n https://github.com/hyperledger/fabric-sdk-py.git
    cd fabric-sdk-py
    git checkout 2ed110b18133339b3cf4bf7246eb6865556f302c
    cd ..
fi

cd fabric-sdk-py
echo "MAKE FFS"
make install
cd ..
curl -sSL https://bit.ly/2ysbOFE | bash -s -- $HLF_VERSION $HLF_VERSION
cp -r ./fabric-sdk-py/hfc ./hfc
cp -r ./fabric-samples/bin/* /bin
rm -rf fabric-sdk-py fabric-samples
