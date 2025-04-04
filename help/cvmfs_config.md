### install sofware on CVMMFS form running image 
- connenct to cvmfs VM ```ssh mazzitel@212.189.145.224```
- change user as root ```sudo su```
- open trascription ```cvmfs_server transaction sft-cygno.infn.it```
- execute the image you like: ```docker run -it --rm -v /cvmfs:/cvmfs gmazzitelli/cygno-wn:v2.4 bash```
- configure eventualy setup like: ```source /cvmfs/sft.cern.ch/lcg/views/LCG_105/x86_64-ubuntu2204-gcc11-opt/setup.sh```
- install your software on cvmfs
- exit form the docker image 
- ```cvmfs_server publish sft-cygno.infn.it```

### expert
- WP6 test: ```cvmfs_server mkfs -w https://rgw.cloud.infn.it:443/cvmfs/sft-cygno.infn.it -u gw,/srv/cvmfs/sft-cygno.infn.it/data/txn,http://cvmfs.wp6.cloud.infn.it:4929/api/v1 -k /etc/publisher_keys/ -o `whoami` sft-cygno.infn.it```
- WP1 pruduction: ```cvmfs_server mkfs -w https://rgw.cloud.infn.it:443/cvmfs/sft-cygno.infn.it -u gw,/srv/cvmfs/sft-cygno.infn.it/data/txn,http://cvmfs.wp6.cloud.infn.it:4929/api/v1 -k /etc/cvmfs/keys/infn.it -o `whoami` sft-cygno.infn.it```
- ```cvmfs_server transaction sft-cygno.infn.it```
- make your change 
- ```cvmfs_server publish sft-cygno.infn.it```
- ```docker run -it -d --rm --name wn -v /cvmfs:/cvmfs gmazzitelli/cygno-wn:v2.4 bash```
- ```docker attach wn```
