FROM python:3.9.0-alpine

ARG PRIVATE_KEY

ENV PRIVATE_KEY ${PRIVATE_KEY}
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH /usr/local/bin
ENV DJANGO_SUPERUSER_PASSWORD admin
ENV DJANGO_SUPERUSER_USERNAME admin
ENV DJANGO_SUPERUSER_EMAIL admin@admin.com
ENV ACCEPT_EULA Y
ENV TIMEZONE CET

EXPOSE 8000

WORKDIR /usr/src/mssql

RUN apk update
RUN apk upgrade
RUN apk add --no-cache g++ libc6-compat libffi-dev openssl-dev bash python3 python3-dev curl mysql mysql-client mariadb-dev mariadb-client

RUN python3 -m ensurepip
RUN pip3 install --no-cache --upgrade pip setuptools

RUN curl -O https://download.microsoft.com/download/e/4/e/e4e67866-dffd-428c-aac7-8d28ddafb39b/msodbcsql17_17.6.1.1-1_amd64.apk
RUN apk add --allow-untrusted msodbcsql17_17.6.1.1-1_amd64.apk
RUN apk add --no-cache unixodbc-dev

COPY Caddyfile /etc/caddy/Caddyfile

WORKDIR /usr/

COPY entrypoint.sh entrypoint.sh

# changes line endings in case the script was copied from windows
RUN tr -d '\015' < entrypoint.sh > entrypoint2.sh
RUN mv -f entrypoint2.sh entrypoint.sh

COPY requirements.txt requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

WORKDIR /usr/src/

COPY . .

CMD [ "/bin/bash", "/usr/entrypoint.sh" ]
