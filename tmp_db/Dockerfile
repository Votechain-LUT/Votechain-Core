FROM mcr.microsoft.com/mssql/server:2019-latest

ENV ACCEPT_EULA Y
ENV SA_PASSWORD Asdf1234
ENV BACKUP_FILE /backups/311.bak
ENV MSSQL_BACKUP_DIR /backups

EXPOSE 1433

RUN mkdir -p /usr/config

WORKDIR /usr/config

COPY . /usr/config



ENTRYPOINT ["bash", "./entrypoint.sh"]
