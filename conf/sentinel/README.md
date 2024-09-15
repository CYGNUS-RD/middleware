# SENTINEL
HTCondor client with python env for data recostruction and file tranfer on S3 storage. 
it need a valid token in /tmp/token
```
      IAM_CLIENT_SECRET: ${IAM_CLIENT_SECRET}
      IAM_CLIENT_ID: ${IAM_CLIENT_ID}
      ENDPOINT_URL: ${ENDPOINT_URL}
      HTC_IP: XXX.XXX.XXX.XXX
```



```
docker run -e HTC_IP=XXX.XXX.XXX.XXX --env-file <( env| cut -f1 -d= ) -v /tmp:/tmp gmazzitelli/sentinel:v0.1
```


# Rebuild image

cd docker
vi Dockerfile #Change what you need
docker build -t gmazzitelli/cygno-st:v2.0.x-cygno . # x is the latest version
docker push gmazzitelli/cygno-st:v2.0.x-cygno

## Change the version on the docker-compose file and then:
docker compose up -d
