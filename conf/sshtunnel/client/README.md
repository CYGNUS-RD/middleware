# SSH reverse Tunnel 

- howto generate the key rsa (do not put any password when proped) 
```
ssh-keygen -t rsa -b 4096 -f xxx_rsa
```
- put the public string xxx_rsa.pub in the remote IP /home/USER/.ssh/authorized_keys

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
       REMOTE_IP: IP # remote ip
    volumes:
       - /home/USER/.ssh/daq_id:/id_rsa # local user with private key 

```
- share remote port with a local client service in a physical machine example using kafka on port 9092 services (LOCALUSER, USER@IP)
- put i in the  /etc/systemd/system/SERVICENAME.service
```
[Unit]
    Description=SSH Tunnel for Kafka
    After=network.target

    [Service]
    Restart=always
    RestartSec=20
    User=standard
    Group=standard
    ExecStart=/usr/bin/ssh -NTC -o ServerAliveInterval=60 -o ExitOnForwardFailure=yes -i /home/LOCALUSER/.ssh/xxx_id -L 0.0.0.0:9092:127.0.0.1:9092 USER@IP


    [Install]
    WantedBy=multi-user.target
```
- sudo systemctl status SERVICENAME
- sudo systemctl daemon-reload
- sudo systemctl start SERVICENAME
- [help on system service](https://www.digitalocean.com/community/tutorials/how-to-use-systemctl-to-manage-systemd-services-and-units)
- to monitor port staus ```sudo lsof -i -P -n | grep LISTEN ```

