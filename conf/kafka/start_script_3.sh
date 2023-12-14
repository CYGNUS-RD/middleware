#!/bin/bash
#eval `oidc-agent`

unset OIDC_SOCK; unset OIDCD_PID; eval oidc-keychain

eval `oidc-agent`

oidc-gen --client-id $IAM_CLIENT_ID --client-secret $IAM_CLIENT_SECRET --rt $REFRESH_TOKEN --manual --issuer $IAM_SERVER --pw-cmd="echo pwd" --redirect-uri="edu.kit.data.oidc-agent:/redirect http://localhost:29135 http://localhost:8080 http://localhost:4242" --scope "openid email wlcg wlcg.groups profile offline_access" $OIDC_AGENT

oidc-token $OIDC_AGENT > /tmp/token

#
# Confiig conndor CYGNO queue
# 173 to the 10 condor
cat > /etc/condor/condor_config.local << EOF 
AUTH_SSL_CLIENT_CAFILE = /etc/pki/ca-trust/source/anchors/htcondor_ca.crt
SCITOKENS_FILE = /tmp/token
SEC_DEFAULT_AUTHENTICATION_METHODS = SCITOKENS
COLLECTOR_HOST = 131.154.98.218.myip.cloud.infn.it:30618
SCHEDD_HOST    = 131.154.98.218.myip.cloud.infn.it
EOF
#
# 
# install crontab
#
#yum install -y crontabs
#crontab -l | { cat; echo "*/10 * * * * eval \`oidc-keychain\` && oidc-token $OIDC_AGENT > /tmp/token"; } | crontab -
