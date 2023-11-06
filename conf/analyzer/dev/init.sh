#!/bin/bash
i=0
d=`date +%Y-%M-%d\ %H:%M:%S`
echo "$d executing init"
WAIT=600
while :
do
	d=`date +%Y-%M-%d\ %H:%M:%S`
	echo "$d loop $i"
# insert your command
	/root/dev/reco2sql.py
	i=$((i+1))
	sleep $WAIT
done
