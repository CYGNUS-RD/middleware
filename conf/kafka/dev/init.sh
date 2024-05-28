#!/bin/bash
echo "------------------------------"
env
echo "------------------------------"
i=0
d=`date +%Y-%M-%d\ %H:%M:%S`
echo "$d executing init"
WAIT=60
while :
do
	d=`date +%Y-%M-%d\ %H:%M:%S`
	echo "$d loop $i"
# insert your command
#	/root/dev/cloud2tape_v2.py -t $BUCKET_TAG -c -q -f 
	i=$((i+1))
	sleep $WAIT
done
