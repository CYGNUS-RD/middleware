#!/bin/bash
env
echo 'STARTING CONUSUMER EVENT-->'
d=`date +%Y-%M-%d\ %H:%M:%S`
echo "started at $d"
/root/dev/consumer_odb_multi.py ${OPTIONS}

