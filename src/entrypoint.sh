#!/bin/sh

/bin/sh ./await.sh

echo "COLLECT STATIC"
python3 manage.py collectstatic --noinput --clear

echo "STARTING UP HTTP LISTENER"
python manage.py runserver 0.0.0.0:$PORT
