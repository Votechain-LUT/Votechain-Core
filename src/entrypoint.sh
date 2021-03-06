#!/bin/bash

/bin/bash ./await.sh

echo "COLLECT STATIC"
python3 manage.py collectstatic --noinput --clear > /dev/null
echo "SEED DATA"
python3 manage.py loaddata --app core core/fixtures/dev_data.json

echo "CREATE HYPERLEDGER FABRIC CHANNEL"
python3 startup_network.py hyperledger/channel hyperledger-network.json
echo "STARTING UP HTTP LISTENER"
python manage.py runserver 0.0.0.0:$PORT
