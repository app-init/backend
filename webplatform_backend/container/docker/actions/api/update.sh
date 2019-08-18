#!/bin/base
echo "Running Update"
sh /home/container/actions/stop.sh
sh /home/container/actions/build.sh
sh /home/container/actions/start.sh
