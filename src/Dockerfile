FROM python:3.7.9-buster

ARG PRIVATE_KEY

ENV PRIVATE_KEY ${PRIVATE_KEY}
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH /usr/local/bin
ENV DJANGO_SUPERUSER_PASSWORD admin
ENV DJANGO_SUPERUSER_USERNAME admin
ENV DJANGO_SUPERUSER_EMAIL admin@admin.com
ENV ACCEPT_EULA Y
ENV TIMEZONE CET
ENV HLF_VERSION 1.4.6
ENV FABRIC_CFG_PATH /usr/src/hyperledger
ENV CHAINCODE_PATH /chaincode/input/src

# installs necessary system packages
RUN apt-get update -y && apt-get upgrade -y && apt-get clean \
    && apt-get install -y software-properties-common dirmngr \
    && apt-key adv --fetch-keys 'https://mariadb.org/mariadb_release_signing_key.asc' \
    && add-apt-repository 'deb [arch=amd64,arm64,ppc64el] https://ftp.icm.edu.pl/pub/unix/database/mariadb/repo/10.5/debian buster main' \
    && apt-get update -y
RUN apt-get install -y libffi-dev python-dev python3-dev libmariadb3 mariadb-client libssl-dev

# ensures pip is installed and upgraded
RUN python3 -m ensurepip
RUN python3 -m pip install --upgrade pip

WORKDIR /usr/src/
COPY . .
COPY hyperledger/chaincode ${CHAINCODE_PATH}

RUN . ./checkout-fabric-sdk.sh

RUN pip3 install --no-cache-dir -r requirements.txt

# changes line endings in case the script was copied from windows
RUN tr -d '\015' < entrypoint.sh > entrypoint2.sh
RUN mv -f entrypoint2.sh entrypoint.sh

CMD [ "/bin/bash", "/usr/src/entrypoint.sh" ]
