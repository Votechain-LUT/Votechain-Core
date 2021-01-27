#!/bin/bash

STATUS=255
i=0

sleep 3s

while [[ $STATUS -ne 52 ]] && [[ $STATUS -ne 1 ]] && [[ $STATUS -ne 0 ]] && [[ $i -lt 60 ]]
do
	let i=i+1
    sleep 1s
	curl --connect-timeout 3 $DATABASE_HOST:$DATABASE_PORT
	STATUS=$?
	echo "status: $STATUS"
	if [[ $STATUS -eq 28 ]]
	then
		let i=i+3
	fi
done

sleep 3s

echo "MIGRATING"
python3 manage.py migrate --noinput
echo "CREATE SUPERUSER"
python3 manage.py createsuperuser --noinput
