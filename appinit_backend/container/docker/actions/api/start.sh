#!/bin/bash -x
if [ ! -e "/home/container/flask.pid" ]; then
  cd /home/cee-tools/api/application/
  echo "Starting '$CEE_TOOLS_SERVICE' on instance '$CEE_TOOLS_INSTANCE'"
  gunicorn app:app -c /home/container/config/gunicorn_config.py

  # if [ ! -e "/home/cee-tools/logs/test.log" ]; then
  #   touch /home/cee-tools/logs/test.log
  #   touch /home/cee-tools/logs/test2.log
  # fi

  # uwsgi --ini /home/container/config/uwsgi.ini &
else
  echo "Already running 'flask' on instance '$CEE_TOOLS_INSTANCE'"
fi
