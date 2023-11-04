# TOKENER
get and refresh 5 minute before the expiration, the token from env variable:
```
      REFRESH_TOKEN: ${REFRESH_TOKEN}
      IAM_CLIENT_SECRET: ${IAM_CLIENT_SECRET}
      IAM_CLIENT_ID: ${IAM_CLIENT_ID}
      IAM_TOKEN_ENDPOINT: ${IAM_TOKEN_ENDPOINT}
      SCOPES: ${SCOPES}
```
and write in /tmp/token to be exploit by other service

``` 
docker run -e IAM_CLIENT_SECRET=... -e IAM_CLIENT_SECRET=... -e IAM_CLIENT_ID:... \
-e IAM_TOKEN_ENDPOINT:.. -e SCOPES=.. -v /tmp:/tmp gmazzitelli/tokener:v0.1
```
or if defined in VM eviroument:
```
docker run --env-file <( env| cut -f1 -d= ) -v /tmp:/tmp gmazzitelli/tokener:v0.1
```
