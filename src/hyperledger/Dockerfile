FROM docker:18.09-dind

WORKDIR /
RUN mkdir /hyperledger
WORKDIR /hyperledger
COPY . .
RUN mv -f dockerd-entrypoint.sh /usr/local/bin/dockerd-entrypoint.sh
EXPOSE 7050 7051 7052 7053 8051 8052 8053 9051 9052 9053 10051 10052 10053

RUN apk update \
    && apk add docker-compose \
    && mkdir -p /compose/docker-compose \
    && ln -s /usr/local/bin/docker-compose /compose/docker-compose
