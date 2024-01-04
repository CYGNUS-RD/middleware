#!/bin/bash
env
echo 'STARTING CONUSUMER EVENT-->'
d=`date +%Y-%M-%d\ %H:%M:%S`
echo "started at $d"
/root/dev/consumer_event_s3.py ${OPTIONS}

