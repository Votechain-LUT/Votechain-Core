#!/bin/bash

/bin/bash ./await.sh

echo "COLLECT STATIC"
python3 manage.py collectstatic --noinput --clear
echo "SEED DATA"
python3 manage.py loaddata --app core core/fixtures/dev_data.json

echo "CREATE HYPERLEDGER FABRIC CHANNEL"
python3 votechain/startup_channel.py hyperledger/channel
echo "STARTING UP HTTP LISTENER"
python manage.py runserver 0.0.0.0:$PORT
