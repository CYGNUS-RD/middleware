# SENTINEL
HTCondor client with python env for data recostruction and file tranfer on S3 storage. 
it need a valid token in /tmp/token
```
      IAM_CLIENT_SECRET: ${IAM_CLIENT_SECRET}
      IAM_CLIENT_ID: ${IAM_CLIENT_ID}
      ENDPOINT_URL: ${ENDPOINT_URL}
```



```
docker run -e HTC_IP=XXX.XXX.XXX.XXX --env-file <( env| cut -f1 -d= ) -v /tmp:/tmp gmazzitelli/sentinel:v0.1
```
