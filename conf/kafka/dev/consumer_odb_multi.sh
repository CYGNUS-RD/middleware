#!/bin/bash
env
echo 'STARTING CONUSUMER EVENT-->'
d=`date +%Y-%M-%d\ %H:%M:%S`
echo "started at $d"
WAIT=60
while :
do
	d=`date +%Y-%M-%d\ %H:%M:%S`
	echo "$d loop $i"
# insert your command
        /root/dev/consumer_odb_multi.py ${OPTIONS}
	i=$((i+1))
	sleep $WAIT
done

