# SSH revers Tunnel 
to share local contaner (LOCAL_APP_NAME) port (LOCAL_PORT) to a remore port (REMOTE_PORT) example:
```
docker run -v /root/.ssh/daq_id:/id_rsa -e REMOTE_PORT=8081 -e LOCAL_APP_NAME=web -e LOCAL_PORT=80 \
-e USER=mazzitel -e REMOTE_IP=grafana.cygno.cloud.infn.it gmazzitelli/sshtunnel

```
example of compose to share the 'web' on port 80 
```
  tunnel:
    restart: always
    image: gmazzitelli/sshtunnel
    container_name: grafana_tunnel
    environment: 
       REMOTE_PORT: 8081
       LOCAL_APP_NAME: web
       LOCAL_PORT: 80 
       USER: mazzitel
       REMOTE_IP: grafana.cygno.cloud.infn.it
    volumes:
       - /root/.ssh/daq_id:/id_rsa 

```
