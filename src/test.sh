#!/bin/bash

/bin/bash ./await.sh

echo "RUNNING TESTS"
python3 manage.py test core.tests --noinput

exit $?
