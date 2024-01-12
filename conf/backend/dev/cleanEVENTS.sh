#!/bin/bash
env
i=0
echo 'STARTING CLEANER-->'
while :
do
	d=`date +%Y-%M-%d\ %H:%M:%S`
	echo "$d loop: $i getting list"
        /root/dev/cleanEVENTS.py 
	echo "Waiting ${WAIT_TIME} sec..."
	i=$((i+1))
        sleep ${WAIT_TIME}
done

