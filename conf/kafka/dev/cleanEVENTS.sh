#!/bin/bash
#echo "CLOUD storage setup: ${OIDC_AGENT}"
#eval `oidc-agent`

#oidc-gen --client-id $IAM_CLIENT_ID --client-secret $IAM_CLIENT_SECRET --rt $REFRESH_TOKEN --manual --issuer $IAM_SERVER --pw-cmd="echo pwd" \
#--redirect-uri="edu.kit.data.oidc-agent:/redirect http://localhost:29135 http://localhost:8080 http://localhost:4242" --scope \
#"openid email wlcg wlcg.groups profile offline_access" $OIDC_AGENT

i=0
while :
do
	d=`date +%Y-%M-%d\ %H:%M:%S`
	echo "$d loop: $i getting list"
        ./cleanEVENTS.py -s sentinel-wlcg
#	cygno_repo ls cygno-data -t EVENTS > EVENTS.txt -s sentinel-wlcg
#        echo "$d loop: $i remouving files"
#        IFS=$'\n';for line in `cat EVENTS.txt`; do cygno_repo rm cygno-data `echo ${line} | cut -d'/' -f2` -t EVENTS -s sentinel-wlcg; done
	echo "Press [CTRL+C] to stop.."
	i=$((i+1))
	sleep 10
done

