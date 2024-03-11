# configuration
- [install docker compose on unbutu](https://docs.docker.com/engine/install/ubuntu/)
- [certbot](https://servicedesk.infn.it/servicedesk/customer/portal/50/INFNCLOUD-540), and then add to crontab: ```0 */12 * * * certbot -q renew```
- ~~192.135.24.159  cygno-jupyter00-dev **certificte, ports, dns**~~
- ~~131.154.96.196  grafana_0  CLOUD-CNAF  **migrated ready to shutdown**~~
- ~~131.154.96.221  sqllngs_0  CLOUD-CNAF  **migrated ready to shutdown**~~
- ~~131.154.96.175  kafka_0  CLOUD-CNAF  **migrated ready to shutdown**~~
- 131.154.99.219  sqllngs CLOUD-CNAF-T1 **up and running**
- 131.154.99.172  grafana CLOUD-CNAF-T1 **up and running**
- 131.154.98.101  kafka CLOUD-CNAF-T1 **up and running**
- 90.147.174.178  backend  BACKBONE-BARI **up and running, work aroud to consume kafka message**
- 90.147.174.164  sentinel  BACKBONE-BARI **up and running**
- 131.154.99.115  gmtest
- 90.147.174.175  cygno_jupyter01  BACKBONE-BARI notebook.cygno.cloud.infn.it  notebook01.cygno.cloud.infn.it
- 192.135.24.178  cygno_jupyter02  BACKBONE-CNAF notebook02.cygno.cloud.infn.it

## to start all services on the VM, please use 
```
cd /home/mazzitel/middleware/conf 
./start_vm.sh 
```

## set up kafka/mongo server
kafka.cygno.cloud.infn.it
kafka server host kfka e mongo slow channal db, docker file in conf/kafka
- https://github.com/CYGNUS-RD/middleware/tree/master/conf/kafka

## set up sentinel server
sentinel.cygno.cloud.infn.it
- https://github.com/CYGNUS-RD/middleware/tree/master/conf/sentinel

## set up grafana and SQL(LNF) server
grafana.cygno.cloud.infn.it, grafana server host grafana in docker file cof/grafna and LNF db in conf/mariadb
- https://github.com/CYGNUS-RD/middleware/tree/master/conf/grafana
- https://github.com/CYGNUS-RD/middleware/tree/master/conf/mariadb
 
## set up SQL (LNGS) server
sql.cygno.cloud.infn.it, host LNGS SQL, analyzer for online reco historization, tape data managment
- https://github.com/CYGNUS-RD/middleware/tree/master/conf/mariadb
- https://github.com/CYGNUS-RD/middleware/tree/master/conf/analizer
- https://github.com/CYGNUS-RD/middleware/tree/master/conf/tape
## set up backend server
backend.cygno.cloud.infn.it, kafka consumer
- https://github.com/CYGNUS-RD/middleware/tree/master/conf/backend

## open issues, to do list
/afs/lnf.infn.it/user/m/mazzitel/www/php/cygno_sql_query.php
aggiornare tutto by name (sql.cygno.cloud.infn.it)


## usefull note
* ODB INFO: [http://lmu.web.psi.ch/docu/manuals/bulk_manuals/software/midas195/html/ODB_Structure.html#ODB_System_Tree](http://lmu.web.psi.ch/docu/manuals/bulk_manuals/software/midas195/html/ODB_Structure.html#ODB_System_Tree)
* LIB INFO: [https://bitbucket.org/tmidas/midas/src/develop/python/](https://bitbucket.org/tmidas/midas/src/develop/python/)
* SSH LNGS: `ssh -p 9023 standard@172.18.9.72 `
* SSH LNF: `ssh -p 9023 standard@spaip.lnf.infn.it` (`ssh -X cygno@spaip.lnf.infn.it -p 9022`)
* CONF: ...
* JUPYTER LNF:  http://spaip.lnf.infn.it:8888/ (not in autostart: `nohup jupyter notebook --no-browser&` )
* JUPYTER LNGS: http://172.18.9.72:8888/ 
* DAQ LNF: https://spaip.lnf.infn.it:8443/
* DAQ LNGS: https://172.18.9.72:8443/


* (sono aperte su entrambe le macchine anche le porte del DAQ e del RTD)
* To access Grafana (Just one for both DBs):
  * 1 - Go to the link: https://grafana.cygno.cloud.infn.it/
  * 2 - Choose "Sign in with IAM"
  * 3 - Use your INFN credentials
  * 4 - Go to the desired Dashboard
  
* [LNF] To access the DB:
  *   1 - Connect to the LNF VPN
  *   2 - Use the following command at the terminal: `ssh -L 8081:131.154.96.196:8081 standard@spaip.lnf.infn.it -p 9023`
  *   3 - DB Address: access the http://localhost:8081/ using the browser
  
* [LNGS] To access DB:
  *   1 - Connect to the LNGS VPN
  *   2 - Use the following command at the terminal: `ssh -L 8081:131.154.96.221:8081 standard@172.18.9.72 -p 9023`
  *   3 - DB Address: access the http://localhost:8081/ using the browser
  

WARNING: directory data/ and file cygno_conf.py (contaning password) are not ignored

## general tips ###
- editor/notebook
```
docker run -it -p 8888:8888 --name editor --user root -w /home/jovyan/work -v $(pwd):/home/jovyan/work jupyter/minimal-notebook
```
- poi Ctrl P /CTRL Q per uscire dalla parte intereattiva 

- ubuntu shell (source faile in conf/storage)
```
docker run -d -v ${PWD}/dev/:/root/dev/ --name myubuntu --net="host" gmazzitelli/myubuntu sleep infinity
docker exec -it myubuntu bash
```

## istallation history and tips:

jupyter configuration (at LNF where root as been istalled as root)
```
sudo chmod 777 /home/software/root_build/etc/notebook/jupyter_notebook_config.py
sudo chmod 777 /home/software/root_build/etc/notebook/
```
first config 
```
jupyter notebook --generate-config
c.NotebookApp.allow_origin = '*'
c.NotebookApp.ip = '0.0.0.0'
c.NotebookApp.password = <password>
```

python setup:

```
pip install testresources
pip install root_numpy
pip install sklearn
pip install Cython
pip install notebook
pip install mysql-connector
pip install git+https://github.com/DODAS-TS/boto3sts
pip install git+https://github.com/CYGNUS-RD/cygno.git
export PYTHONPATH=$PYTHONPATH:$MIDASSYS/python (to set in bashrc/DAQsetup)
sudo pip install -e $MIDASSYS/python --user
```

in middeleware setup for cygno cytron (in dev middelware folder)
```
sudo apt-get install python-numpy
cython cython_cygno.pyx
cythonize -a -i cython_cygno.pyx
```

cloud token https://github.com/CYGNUS-RD/cygno; http://repo.data.kit.edu/ (if repository unreachble eg ubunto 20.04)
```
sudo apt-key adv --keyserver hkp://pgp.surfnet.nl --recv-keys ACDFB08FDC962044D87FF00B512839863D487A87
vi /etc/apt/sources.list
```
add
```
deb https://repo.data.kit.edu/ubuntu/20.04 ./
sudo apt-get install oidc-agent
```
## gestione del router 
https://wiki.ubuntu-it.org/Sicurezza/Nftables
```
IP LNGS: mazzitel@172.18.9.72
```
* Configurazione Virtual host e routing /etc/nftables.conf
* Restart seervice: ```nft -f /etc/nftables.conf```
* Configurazione fixed host: /etc/dhcp/fixed-addr.conf
* Restart service: ```systemctl restart isc-dhcp-server.service```
* ip volatili: /var/lib/dhcp/dhcpd.leases


```
#host lap-mazzitelli {hardware ethernet d0:c0:bf:2e:6b:4c; fixed-address 192.168.99.10; }
host daq-server1 {hardware ethernet 3c:ec:ef:6c:df:ac; fixed-address 192.168.99.10; }
host daq-server2 {hardware ethernet 3c:ec:ef:6c:e0:d8; fixed-address 192.168.99.11; }
host pc-windows {hardware ethernet e4:54:e8:83:25:c1; fixed-address 192.168.99.12; }
host hv-iseg {hardware ethernet 00:80:a3:e1:9c:01; fixed-address 192.168.99.13; }
host hv-caen {hardware ethernet 00:90:fb:66:2f:2c; fixed-address 192.168.99.14; }
#host slow-mscb399 {hardware ethernet 00:50:c2:46:d1:8f; fixed-address 192.168.99.15; } # scs rotto
host slow-mscb399 {hardware ethernet 00:50:c2:46:d4:16; fixed-address 192.168.99.15; }
host gas-system {hardware ethernet 00:03:27:11:c3:53; fixed-address 192.168.99.20; }

```

## HTCondor + Kubernetes

#  How to add created WN (worker nodes) to another existent Condor Queue:

1. ssh the WN you want to move from one Queue to another;

2. Then, create the config file:
  ```
  vi /etc/condor/condor_config.local
  ```
3. Add the line:
  ```
  CONDOR_HOST = <IP_Kubernetes>
  ```

4. Then, run the command:

  ```
  condor_reconfig
  ```


## Database SQL (MariaDB)
 Installation and problem solve of the Database can be found here: [README.md](https://github.com/CYGNUS-RD/middleware/blob/master/conf/mariadb/README.md)

