#!/bin/bash
i=0
while :
do
	d=`date +%Y-%M-%d\ %H:%M:%S`
	echo "$d loop: $i"
	./consumer_event_s3.py -v
	echo "Press [CTRL+C] to stop.."
	i=$((i+1))
	sleep 600
done
