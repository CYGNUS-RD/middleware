to get tocken 
$(curl -s -u ${IAM_CLIENT_ID}:${IAM_CLIENT_SECRET} \
    	-d scopes="\"${SCOPES}"\" -d grant_type=refresh_token \
    	-d refresh_token=${REFRESH_TOKEN} ${IAM_TOKEN_ENDPOINT})

docker run -it \
-e RUCIO_ACCOUNT=mazzitel \
​​-e TOKEN=$(./gettoken.sh) \
-v .:/data\
harbor.cloud.infn.it/testbed-dm/rucio-client-cygno:v2 -- bash


docker run -it -e RUCIO_ACCOUNT=mazzitel -e TOKEN=$(./gettoken.sh) -v ${PWD}:/data harbor.cloud.infn.it/testbed-dm/rucio-client-cygno:v2 -- bash
