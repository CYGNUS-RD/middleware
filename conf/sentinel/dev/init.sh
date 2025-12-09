#!/bin/bash
i=0
d=`date +%Y-%M-%d\ %H:%M:%S`

if [ -d /root/submitJobs ]; then
  echo "submitJobs found"
else
  mkdir /root/submitJobs
fi

#cd /root/submitJobs
cd /tmp

if [ -f /root/dev/${DFPANDAS}.csv ]; then
   echo "copying df"
   cp /root/dev/${DFPANDAS}.csv /root/submitJobs/
else
   echo "df will be create"
fi

echo "$d running full reco..."


#CMD ["python", "-u", "main.py"]

sleep ${WAITTIME}

python3 -u /root/dev/fullRecoSentinel_v3.00.py ${STARTRUN} -e ${ENDRUN} -j ${NCORE} -i ${MAXIDLE} -t ${TAG} -f ${RECOPATH} -o ${DFPANDAS} -s ${DRAIN} -v >> /root/dev/log/reco${DFPANDAS}.log  2>&1

#WAIT=3600
#while :
#do
#	d=`date +%Y-%M-%d\ %H:%M:%S`
#	echo "$d loop $i"
# insert your command
#	i=$((i+1))
#	sleep $WAIT
#done
