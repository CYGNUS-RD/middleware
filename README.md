# Middle Ware

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
  * 1 - Go to the link: https://131.154.96.196:3000/
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

### istallation history and tips:

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
### gestione del router 
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
