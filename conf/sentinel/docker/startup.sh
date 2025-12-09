#!/bin/bash

#
# confiig conndor CYGNO queue
#
#cat > /etc/condor/condor_config.local << EOF 
#AUTH_SSL_CLIENT_CAFILE = /etc/pki/ca-trust/source/anchors/htcondor_ca.crt
#SCITOKENS_FILE = /tmp/token
#SEC_DEFAULT_AUTHENTICATION_METHODS = SCITOKENS
#COLLECTOR_HOST = ${HTC_IP}.myip.cloud.infn.it:30618
#SCHEDD_HOST = ${HTC_IP}.myip.cloud.infn.it
#EOF


export BEARER_TOKEN=$(cat /tmp/token)

bash_file=/root/init.sh
if [ -e "$bash_file" ]; then
    echo "excuting init file"
    $bash_file &
else 
    echo "${bash_file} does not exist"
fi 
env
echo "STARTNG SENTINEL-->"
tail -f /tmp/token
