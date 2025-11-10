### publishing sofware on CVMFS for a specific image (2.4 in the following) 
- connenct to cvmfs VM ```ssh mazzitel@212.189.145.224``` stadalone publisher or ```ssh mazzitel@2notebook00.cygno.cloud.infn.it```
- change user as root ```sudo su```
- open trascription ```cvmfs_server transaction sft-cygno.infn.it```
- execute the image you like (e.g.): ```docker run -it --rm -v /cvmfs:/cvmfs gmazzitelli/cygno-wn:v2.4 bash```
- configure eventualy setup like (e.g): ```source /cvmfs/sft.cern.ch/lcg/views/LCG_105/x86_64-ubuntu2204-gcc11-opt/setup.sh```
- install your software on cvmfs
- exit form the docker image 
- ```cvmfs_server publish sft-cygno.infn.it```

WARNING: Be careful not to have the /cvmfs resource in use by any process. This means you should either exit the /cvmfs directory if you have entered it, or ensure the Docker container is removed. Using the --rm option will automatically remove the container upon exit.

### publishing python library for a specific os relese (ex export PYTHONPATH="/mnt/py/Ubuntu22.04_Py3.11.9")
- connenct to ```ssh mazzitel@2notebook00.cygno.cloud.infn.it```
- change user as root ```sudo su```
- ```cd /home/mazzitel/jupyterhub/CYGNO/package```
- ```cvmfs_server transaction sft-cygno.infn.it; docker-compose up -d; docker exec -it py_assets bash```
- Now you have some options: <br />
    - To install new package: add the package name into /tmp/requirements.txt and then ```pip install -r /tmp/requirements.txt --no-deps -t $PYTHONPATH/ ``` <br />
    - To reinstall existing package `pip install --force-reinstall -v "MySQL_python==1.2.2" --no-deps -t $PYTHONPATH/` (MySQL_python==1.2.2 is an example)
- After succesful installation do `exit`
- ```docker-compose down ; cvmfs_server publish sft-cygno.infn.it```

### expert
- [client configuration](https://confluence.infn.it/spaces/INFNCLOUD/pages/638124033/Configuration+of+clients+for+.infn.it+repos+hosted+on+the+production+managed+by+WP1+infrastructure+sharing+the+same+public+key)
- [publisher configuration WP6/WP1](https://confluence.infn.it/spaces/INFNCLOUD/pages/112428477/CVMFS+publisher+howto+create+an+host+publisher) 
- WP6 test: ```cvmfs_server mkfs -w https://rgw.cloud.infn.it:443/cvmfs/sft-cygno.infn.it -u gw,/srv/cvmfs/sft-cygno.infn.it/data/txn,http://cvmfs.wp6.cloud.infn.it:4929/api/v1 -k /home/mazzitel/keys_w6_publisher/ -o `whoami` sft-cygno.infn.it```
- WP1 pruduction: ```cvmfs_server mkfs -w https://rgw.cloud.infn.it:443/cvmfs-prod/sft-cygno.infn.it -u gw,/srv/cvmfs/sft-cygno.infn.it/data/txn,http://cvmfs.cloud.infn.it:4929/api/v1 -k /home/mazzitel/cvmfs_key/keys_w1_publisher/ -o `whoami` sft-cygno.infn.it```
  <!--```cvmfs_server mkfs -w https://rgw.cloud.infn.it:443/cvmfs/sft-cygno.infn.it -u gw,/srv/cvmfs/sft-cygno.infn.it/data/txn,http://cvmfs.wp6.cloud.infn.it:4929/api/v1 -k /home/mazzitel/keys_w1_publisher/ -o `whoami` sft-cygno.infn.it``` -->
- ```cvmfs_server transaction sft-cygno.infn.it```
- make your change 
- ```cvmfs_server publish sft-cygno.infn.it```
- ```docker run -it -d --rm --name wn -v /cvmfs:/cvmfs $PWD/soft_test:/home/root gmazzitelli/cygno-wn:v2.4 bash```
- ```docker attach wn```
