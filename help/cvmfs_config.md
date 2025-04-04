### install sofware on CVMMFS form running image 
- connenct to cvmfs VM ```ssh mazzitel@212.189.145.224```


### expert
- WP6 test: ```cvmfs_server mkfs -w https://rgw.cloud.infn.it:443/cvmfs/sft-cygno.infn.it -u gw,/srv/cvmfs/sft-cygno.infn.it/data/txn,http://cvmfs.wp6.cloud.infn.it:4929/api/v1 -k /etc/publisher_keys/ -o `whoami` sft-cygno.infn.it```
- WP1 pruduction: ```cvmfs_server mkfs -w https://rgw.cloud.infn.it:443/cvmfs/sft-cygno.infn.it -u gw,/srv/cvmfs/sft-cygno.infn.it/data/txn,http://cvmfs.wp6.cloud.infn.it:4929/api/v1 -k /etc/cvmfs/keys/infn.it -o `whoami` sft-cygno.infn.it```
- ```cvmfs_server transaction sft-cygno.infn.it```
- make your change 
- ```cvmfs_server publish sft-cygno.infn.it```
