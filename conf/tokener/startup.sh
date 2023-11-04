#!/bin/bash
i=0
# env
echo "STARTNG TOKENER-->"
while :
do
	d=`date +%Y-%M-%d\ %H:%M:%S`
	RESPONSE="$(curl -s -u ${IAM_CLIENT_ID}:${IAM_CLIENT_SECRET} \
    	-d scopes="\"${SCOPES}"\" -d grant_type=refresh_token \
    	-d refresh_token=${REFRESH_TOKEN} ${IAM_TOKEN_ENDPOINT})"
	echo $RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" >/tmp/token
	EXPIRE=`echo $RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['expires_in'])"`
	WAIT=$(($EXPIRE-300)) # refresh token after
	echo "$d next refreshing token in $WAIT sec, loop $i"
	i=$((i+1))
	sleep $WAIT
done
