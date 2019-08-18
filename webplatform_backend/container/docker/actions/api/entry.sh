#!/bin/bash -x
if [ ! -e "/home/error.log" ]; then
  touch /home/error.log
fi

rm -rf /home/container/flask.pid

sh /home/container/actions/start.sh

tail -f /home/cee-tools/logs/debug.log
