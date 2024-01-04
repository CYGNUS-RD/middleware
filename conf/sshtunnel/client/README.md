# SSH reverse Tunnel 
share local contaner (LOCAL_APP_NAME) port (LOCAL_PORT) to a remore port (REMOTE_PORT) via ssh tunnel, example:
```
docker run -v <rsa file>:/id_rsa -e REMOTE_PORT=<port> -e LOCAL_APP_NAME=<service name> -e LOCAL_PORT=<port> \
-e USER=<user> -e REMOTE_IP=<ip> gmazzitelli/sshtunnel

```
example of compose file to share the 'web' app listening on port 80 on remote port 8081 of grafana.cygno.cloud.infn.it
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
