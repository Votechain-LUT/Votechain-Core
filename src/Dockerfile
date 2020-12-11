FROM caddy:2.1.1-alpine

ARG PRIVATE_KEY

ENV PRIVATE_KEY ${PRIVATE_KEY}}
ENV PYTHONUNBUFFERED 1
ENV ACCEPT_EULA Y

RUN apk update
RUN apk upgrade
RUN apk add --no-cache g++
RUN apk add --no-cache libc6-compat
RUN apk add bash

RUN apk add python3 python3-dev
RUN python3 -m ensurepip
RUN pip3 install --no-cache --upgrade pip setuptools

RUN apk add --no-cache curl
RUN curl -O https://download.microsoft.com/download/e/4/e/e4e67866-dffd-428c-aac7-8d28ddafb39b/msodbcsql17_17.6.1.1-1_amd64.apk
RUN apk add --allow-untrusted msodbcsql17_17.6.1.1-1_amd64.apk
RUN apk add --no-cache unixodbc-dev

COPY Caddyfile /etc/caddy/Caddyfile

WORKDIR /usr/src/

RUN mkdir -p static
COPY . .

# changes line endings in case the script was copied from windows
RUN tr -d '\015' < entrypoint.sh > entrypoint2.sh
RUN mv -f entrypoint2.sh entrypoint.sh

RUN pip3 install --no-cache-dir -r requirements.txt

CMD [ "/bin/bash", "entrypoint.sh" ]
