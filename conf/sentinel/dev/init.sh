#!/bin/bash
i=0
d=`date +%Y-%M-%d\ %H:%M:%S`

mkdir /root/submitJobs

echo "$d executing init"

/root/dev/fullRecoSentinel_v1.02.py ${STARTRUN} -o ${DFPANDAS} -v


#WAIT=3600
#while :
#do
#	d=`date +%Y-%M-%d\ %H:%M:%S`
#	echo "$d loop $i"
# insert your command
#	i=$((i+1))
#	sleep $WAIT
#done
