#!/bin/bash

export STATUS=1
i=0

while [[ $STATUS -ne 0 ]] && [[ $i -lt 60 ]]; do
	i=$i+1
    sleep 1
	/opt/mssql-tools/bin/sqlcmd -t 1 -U sa -P $SA_PASSWORD -Q "select 1" >> /dev/null
	STATUS=$?
done

if [[ $STATUS -ne 0 ]]; then
	echo "Error: MSSQL SERVER took more than 60 seconds to start up"
	exit 1
fi

echo "Building the database from startup.sql"
/opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P $SA_PASSWORD -d master -i startup.sql
