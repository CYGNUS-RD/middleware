# SSH reverse Tunnel 
share local contaner (LOCAL_APP_NAME) port (LOCAL_PORT) to a remore port (REMOTE_PORT) via ssh tunnel, example:
```
docker run -v <rsa file>:/id_rsa -e REMOTE_PORT=<port> -e LOCAL_APP_NAME=<service name> -e LOCAL_PORT=<port> \
-e USER=<user> -e REMOTE_IP=<ip> gmazzitelli/sshtunnel

```
- client side example of compose file to share the 'web' app listening on port 80 on remote port 8081 of grafana.cygno.cloud.infn.it
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
- server side in a physical machine example using kafka on port 9092
```
[Unit]
    Description=SSH Tunnel for Kafka
    After=network.target

    [Service]
    Restart=always
    RestartSec=20
    User=standard
    Group=standard
    ExecStart=/usr/bin/ssh -NTC -o ServerAliveInterval=60 -o ExitOnForwardFailure=yes -i /home/standard/.ssh/daq_id -L 0.0.0.0:9092:127.0.0.1:9092 user@ip


    [Install]
    WantedBy=multi-user.target
```
