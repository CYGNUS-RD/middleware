set contaner variable to 

* port 6033, 8081, 3000
* docker_storage_size = 200
* set variable MYSQL_ROOT_PASSWORD, MYSQL_PASSWORD, GF_SECURITY_ADMIN_PASSWORD
* i container yml files sono in /opt/myprj
* (sudo docker down; sudo docker-compose up -d)
* nel folder grafana 
```
sudo chown -R 472:472 /opt/myprj/grafana/
sudo openssl req -x509 -sha256 -days 3560 -nodes  -newkey rsa:2048 -subj "/CN=cygnoC=IT/L=LNGS"  -keyout grafana.key -out grafana.crt
```
