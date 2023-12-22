# configuration
- [install docker compose on unbutu](https://docs.docker.com/engine/install/ubuntu/)
- [certbot](https://servicedesk.infn.it/servicedesk/customer/portal/50/INFNCLOUD-540)
- 192.135.24.159  cygno-jupyter00-dev **certificte, ports, dns**
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

# to start all services on the VM, please use 
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
grafana.cygno.cloud.infn.it
grafana server host grafana in docker file cof/grafna and LNF db in conf/mariadb
- https://github.com/CYGNUS-RD/middleware/tree/master/conf/grafana
- https://github.com/CYGNUS-RD/middleware/tree/master/conf/mariadb
 
## set up SQL (LNGS) server
sql.cygno.cloud.infn.it host LNGS SQL, analyzer for online reco historization, tape data managment
- https://github.com/CYGNUS-RD/middleware/tree/master/conf/mariadb
- https://github.com/CYGNUS-RD/middleware/tree/master/conf/analizer
- https://github.com/CYGNUS-RD/middleware/tree/master/conf/tape

## open issues
/afs/lnf.infn.it/user/m/mazzitel/www/php/cygno_sql_query.php

