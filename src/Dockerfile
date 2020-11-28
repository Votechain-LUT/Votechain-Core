FROM caddy:2.1.1-alpine

ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH /usr/local/bin
ENV DJANGO_SUPERUSER_PASSWORD admin
ENV DJANGO_SUPERUSER_USERNAME admin
ENV DJANGO_SUPERUSER_EMAIL admin@admin.com
ENV DATABASE_USER sa
ENV DATABASE_PASSWORD Asdf1234
ENV ACCEPT_EULA Y

EXPOSE 8000

RUN apk update
RUN apk add --no-cache g++
RUN apk add --no-cache libc6-compat

RUN apk add python3 python3-dev
RUN python3 -m ensurepip
RUN pip3 install --no-cache --upgrade pip setuptools

RUN apk add --no-cache curl
RUN curl -O https://download.microsoft.com/download/e/4/e/e4e67866-dffd-428c-aac7-8d28ddafb39b/msodbcsql17_17.6.1.1-1_amd64.apk
RUN apk add --allow-untrusted msodbcsql17_17.6.1.1-1_amd64.apk
RUN apk add --no-cache unixodbc-dev

COPY Caddyfile /etc/caddy/Caddyfile

WORKDIR /usr/src/

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD [ "/bin/sh", "entrypoint.sh" ]
