#!/bin/bash
env
#
# confiig conndor CYGNO queue
#
cat > /etc/condor/condor_config.local << EOF 
AUTH_SSL_CLIENT_CAFILE = /etc/pki/ca-trust/source/anchors/htcondor_ca.crt
SCITOKENS_FILE = /tmp/token
SEC_DEFAULT_AUTHENTICATION_METHODS = SCITOKENS
COLLECTOR_HOST = ${HTC_IP}.myip.cloud.infn.it:30618
SCHEDD_HOST = ${HTC_IP}.myip.cloud.infn.it
EOF
#!/bin/bash
bash_file=/root/init.sh
if [ -e "$bash_file" ]; then
    echo "excuting init file"
    $bash_file &
else 
    echo "${bash_file} does not exist"
fi 

echo "STARTNG SENTINEL-->"
tail -f /tmp/token
