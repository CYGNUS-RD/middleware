# kafka container 
## network and services
- all port of the VM are closed
- **editor** service under kafka port 8890 (closed, tunnel needed), to see editor tocken provide dommand: ```docker exec -it editor jupyter server list```
- **nginx** service running on port 80
- **sentinel, sentinel2, sentine3** service running on port 9618
- **zoiper, kafka** services running on port 2181 and 9093
- **mongo, mongoexpers** sercies running on port 27017 and 8081 
## restart kafka (only)
```
cd /home/mazzitel/middleware/conf/kafka
docker stop kafka zookeeper
docker rm kafka zookeeper
docker-compose up -d
```  
