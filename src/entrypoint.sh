#!/bin/sh

STATUS=1
i=0

while [[ $STATUS -ne 52 ]] && [[ $i -lt 60 ]]; do
	let i=i+1
    sleep 1
	curl $DATABASE_HOST:1433
	STATUS=$?
done

echo "MIGRATING"
python manage.py migrate --noinput
echo "CREATING SUPERUSER"
python manage.py createsuperuser --noinput
echo "STARTING UP HTTP LISTENER"
python manage.py runserver 0.0.0.0:8000
