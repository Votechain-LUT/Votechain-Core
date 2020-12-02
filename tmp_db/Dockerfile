FROM mcr.microsoft.com/mssql/server:2019-latest

ENV ACCEPT_EULA Y

RUN mkdir -p /usr/config

WORKDIR /usr/config

COPY . .

ENTRYPOINT ["bash", "./entrypoint.sh"]
