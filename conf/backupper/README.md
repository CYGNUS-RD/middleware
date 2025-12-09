# BACKUPPER
backup a local folder/container service and copy it a specific location in S3:

```
file2s3_fromHTTPtoken.py <filename> $IAM_CLIENT_ID $IAM_CLIENT_SECRET 
```
exploit tocken in /tmp/token obtained by tokener service, example:

``` 
# docker run -d --name backupper  -e BCK_START_NAME='sql' -e IAM_CLIENT_ID=${IAM_CLIENT_ID} -e IAM_CLIENT_SECRET=${IAM_CLIENT_SECRET} -v /var/lib/docker/volumes/sql_dbdata/_data/:/root/data/ -v /tmp/:/tmp/ gmazzitelli/backupper:v0.1
# docker run -d --name backupper -e BCK_START_NAME='grafana' -e IAM_CLIENT_ID=${IAM_CLIENT_ID} -e IAM_CLIENT_SECRET=${IAM_CLIENT_SECRET} -v /var/lib/docker/volumes/grafana_dbdata/_data/:/root/data/ -v /tmp/:/tmp/ gmazzitelli/backupper:v0.1
docker run -d --name backupper  -e BCK_START_NAME='sql' -v /var/lib/docker/volumes/sql_dbdata/_data/:/root/data/ -v /tmp/:/tmp/ gmazzitelli/backupper:v0.2
```
# tips
exploiting VM eviroument:
```
docker run --env-file <( env| cut -f1 -d= ) -v /tmp:/tmp <image>
```
editor
```
docker run -d --name editor -p 10000:8888 -v /home/mazzitel/middleware/conf/:/home/jovyan/work jupyter/scipy-notebook 
```
