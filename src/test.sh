#!/bin/sh

/bin/sh ./await.sh

echo "RUNNING TESTS"
python3 manage.py test core.tests --noinput

exit $?
