#!/bin/bash
env
i=0
d=`date +%Y-%M-%d\ %H:%M:%S`
echo "$d executing init"

#if [ -e "$BUCKET_TAG" ]; then
#    echo "beckuping tag $BUCKET_TAG"
#else 
#    echo "bucket not does not exist assuming"
#    export BUCKET_TAG='LNGS'
#    echo "beckuping tag $BUCKET_TAG"
#fi

WAIT=900
while :
do
	d=`date +%Y-%M-%d\ %H:%M:%S`
	echo "$d loop $i"
# insert your command
       #export BEARER_TOKEN=$(cat /tmp/tape_token)
	/root/dev/cloud2tape_userpass.py -t $BUCKET_TAG -c -q -f 
	i=$((i+1))
	sleep $WAIT
done
