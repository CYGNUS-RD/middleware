####uso del container RUCIO dato da WP6 CANF con username privileggiata 'mazzitel'

to get token (script gettoken.sh) 
```$(curl -s -u ${IAM_CLIENT_ID}:${IAM_CLIENT_SECRET} \
    	-d scopes="\"${SCOPES}"\" -d grant_type=refresh_token \
    	-d refresh_token=${REFRESH_TOKEN} ${IAM_TOKEN_ENDPOINT})```

```docker run -it --rm --name rucio-mazzitel -e RUCIO_ACCOUNT=mazzitel -e TOKEN=$(./gettoken.sh) -v ${PWD}:/data -v /tmp:/tmp harbor.cloud.infn.it/testbed-dm/rucio-client-cygno:v3  -- bash```

+ un altro modo che sfrutta il token fatto dal "tokener" nella /tmp

```docker compose up -d;
   docker attach rucio-mazzitel=```

+ e poi il solito comando ```rucio whoami```

####setup per accesso a shell come daq

+ vedi docker-compose e README file in rucio_cmd_script/script

```docker run --rm -it --name rucio-daq  -v /root/.rucio.cfg:/app/.rucio.cfg -v ./rucio_cmd_script/:/app/rucio_cmd_script  gmazzitelli/rucio-shell```

