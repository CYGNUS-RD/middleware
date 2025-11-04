# Setting up

Install the following libraries:
- oidc-agent. See how to install this package as for the [cygno-libs](https://github.com/CYGNUS-RD/cygno?tab=readme-ov-file#install-the-cygno-library)
- Boto3 e Botocore
```pip install boto3==1.35.0 botocore==1.35.99```
- rclone. See [Install rclone](https://rclone.org/install/). <br />
Basically  ``` sudo -v ; curl https://rclone.org/install.sh | sudo bash ```

# Copy files from local PC to cnaf-storage
- Copy the file cygno_gsetup.sh from /cvmfs/sft-cygno.infn.it/config/ in the notebook into local folder
- run ```./cygno_gsetup.sh```
- Mount the bucket you want into a local folder you desire <br />
```mkdir  /folder-in-desired-path-and-name```<br />
```rclone mount cnaf-storage:bucket ./folder-in-desired-path-and-name/ --daemon```<br />
for example
```rclone mount cnaf-storage:cygno-analysis ./Mettoqui/ --daemon```<br />
