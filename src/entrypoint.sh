#!/bin/sh

STATUS=1
i=0

sleep 3s

while [[ $STATUS -ne 52 ]] && [[ $i -lt 60 ]]
do
	let i=i+1
    sleep 1s
	curl $DATABASE_HOST:1433
	STATUS=$?
done

sleep 3s

echo "MIGRATING"
python3 manage.py migrate --noinput
echo "CREATE SUPERUSER"
python3 manage.py createsuperuser --noinput
echo "COLLECT STATIC"
python3 manage.py collectstatic --noinput --clear

echo "STARTING UP HTTP LISTENER"
python manage.py runserver 0.0.0.0:8000
