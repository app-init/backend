#!/bin/bash -x
if [ -e "/home/container/flask.pid" ]; then
  PID=$(cat /home/container/flask.pid)
  CHECK=$(ps -p $PID | tail -n +2 | awk '{ print $1 }')

  if [ "$CHECK" == "$PID" ]; then
    echo "Stopping '$CEE_TOOLS_SERVICE' on instance '$CEE_TOOLS_INSTANCE'"
    kill -s TERM $PID

    # while true; do
    #   PID=$(cat /home/container/flask.pid)
    #   CHECK=$(ps -p $PID | tail -n +2 | awk '{ print $1 }')
    #
    #   if [ "$CHECK" != "$PID" ]; then
    #     rm -f /home/container/flask.pid
    #     break
    #   fi
    # done
  else
    echo "Already killed '$CEE_TOOLS_SERVICE' on instance '$CEE_TOOLS_INSTANCE'"
    rm -f /home/container/flask.pid
  fi
else
  echo "Already killed '$CEE_TOOLS_SERVICE' on instance '$CEE_TOOLS_INSTANCE'"
fi
