# Setting up
rclone program is widely utilized to sync and share remote disks and cloud ones to personal use PC. Many higher level programs employ rclone underneath. This tool can be used also to locally mount google drive, one drive and other cloud storage locations. <br />
Install the following libraries:
- oidc-agent. See how to install this package as for the [cygno-libs](https://github.com/CYGNUS-RD/cygno?tab=readme-ov-file#install-the-cygno-library)
- Boto3 e Botocore
```pip install boto3==1.35.0 botocore==1.35.99```
- rclone. See [Install rclone](https://rclone.org/install/). <br />
Basically  ``` sudo -v ; curl https://rclone.org/install.sh | sudo bash ```

# Copy files from local PC to cnaf-storage
- Copy the file cygno_gsetup.sh from the path /cvmfs/sft-cygno.infn.it/config/ in the jupyter notebook (01 or 02) into local a folder (Giovanni does not fully agree)
- On your PC in the folder where you copied cygno_gsetup.sh, run ```./cygno_gsetup.sh``` (it does not matter which folder you are. If you are a WLS user do the instructions until the mount one in a pure Linux folder)
- If the program asks anything simply press enter
- Mount the bucket you want into a local folder you desire <br />
```mkdir  /folder-in-desired-path-and-name```<br />
```rclone mount cnaf-storage:bucket ./folder-in-desired-path-and-name/ --daemon```<br />
for example
```rclone mount cnaf-storage:cygno-analysis ./Mettoqui/ --daemon```<br />
- Now the desired bucket is mounted into a local folder and you can easily copy from terminal any file with cp command

Warning:<br />
- If you turn off your PC, the mount will command will have to be repeated at restart (EXPERT: unless you play with fstab or bash_profile files)
- The token generated during ```./cygno_gsetup.sh``` expires in 12 days. After expiration, you do not need to repeat everything:
  -  Use ```oidc-add cygno``` and follow the instructions and just press enter when asked about password.
  -  After you get a success do ```oidc-token > ~/.cygno_token ```
