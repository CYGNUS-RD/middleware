#/bin/sh
source /home/mazzitel/.test_env
RESPONSE="$(curl -s -u ${MY_IAM_CLIENT_ID}:${MY_IAM_CLIENT_SECRET} \
    	-d scopes="\"${SCOPES}"\" -d grant_type=refresh_token \
    	-d refresh_token=${MY_REFRESH_TOKEN} ${MY_IAM_SERVER}/token)"
echo $RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 
