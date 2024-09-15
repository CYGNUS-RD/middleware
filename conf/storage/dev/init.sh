#!/bin/bash
echo "------------------------------"
env
echo "------------------------------"
i=0
d=`date +%Y-%M-%d\ %H:%M:%S`
echo "$d executing init"
unset OIDC_SOCK; unset OIDCD_PID; eval `oidc-keychain`
oidc-gen --client-id $IAM_CLIENT_ID --client-secret $IAM_CLIENT_SECRET --rt $REFRESH_TOKEN --manual --issuer $IAM_SERVER --pw-cmd="echo pwd" --redirect-uri="edu.kit.data.oidc-agent:/redirect http://localhost:34429 http://localhost:8080 http://localhost:4242" --scope "$SCOPES" infncloud-iam
export TOKEN=$(oidc-token --aud="object" infncloud-iam)
WAIT=60

#while :
#do
#	d=`date +%Y-%M-%d\ %H:%M:%S`
#	echo "$d loop $i"
# insert your command
#	/root/dev/cloud2tape_v2.py -t $BUCKET_TAG -c -q -f 
#	i=$((i+1))
#	sleep $WAIT
#done
