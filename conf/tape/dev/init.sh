#!/bin/bash
i=0
d=`date +%Y-%M-%d\ %H:%M:%S`
echo "$d executing init"
WAIT=900
while :
do
	d=`date +%Y-%M-%d\ %H:%M:%S`
	echo "$d loop $i"
# insert your command
	/root/dev/cloud2tape_v2.py -c -q -f
	i=$((i+1))
	sleep $WAIT
done
