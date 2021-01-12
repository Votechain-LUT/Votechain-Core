#!/bin/sh

/bin/sh ./await.sh

echo "COLLECT STATIC"
python3 manage.py collectstatic --noinput --clear
echo "SEED DATA"
python3 manage.py loaddata --app core core/fixtures/dev_data.json

echo "STARTING UP HTTP LISTENER"
python manage.py runserver 0.0.0.0:$PORT
