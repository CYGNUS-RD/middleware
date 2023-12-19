# configuration
- [install docker compose on unbutu](https://docs.docker.com/engine/install/ubuntu/)
- 192.135.24.159  cygno-jupyter00-dev **certificte, ports, dns**
- 131.154.96.196  grafana_0  CLOUD-CNAF  **certificte**
- 131.154.96.221  sqllngs_0  CLOUD-CNAF  **ready to migrate**
- 131.154.96.175  kafka_0  CLOUD-CNAF  **migrated (can be shutdown)**
- 131.154.99.219  sqllngs CLOUD-CNAF-T1
- 131.154.99.172  grafana CLOUD-CNAF-T1
- 131.154.98.101  kafka CLOUD-CNAF-T1 **up and running**
- 90.147.174.178  backend  BACKBONE-BARI **up and running, work aroud to consume kafka message**
- 90.147.174.164  sentinel  BACKBONE-BARI **up and running**
- 131.154.99.115  gmtest
- 90.147.174.175  cygno_jupyter01  BACKBONE-BARI notebook.cygno.cloud.infn.it  notebook01.cygno.cloud.infn.it
- 192.135.24.178  cygno_jupyter02  BACKBONE-CNAF notebook02.cygno.cloud.infn.it
## set up kafka/mongo server 
- https://github.com/CYGNUS-RD/middleware/tree/master/conf/kafka

## set up sentinel server
- https://github.com/CYGNUS-RD/middleware/tree/master/conf/sentinel
