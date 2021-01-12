#!/bin/sh

containers=$(docker ps -a -q)

if test -z "$containers"
then
    echo "Nothing to cleanup"
else
    docker stop $(echo $containers)
    docker rm $(echo $containers)
fi

exit 0
