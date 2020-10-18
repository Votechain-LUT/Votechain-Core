#!/bin/bash

# script which awaits for initialisation of an sql server instance and runs startup script
/bin/bash ./startup.sh &

# runs the sql server instance
/opt/mssql/bin/sqlservr
