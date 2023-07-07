### how to install oidc on linux
* go to the repo http://repo.data.kit.edu/
* check your ubuntu relese `lsb_release -a`
* example of ubuntu 20.04:
<code>
curl repo.data.kit.edu/repo-data-kit-edu-key.gpg | gpg --dearmor > /etc/apt/trusted.gpg.d/kitrepo-archive.gpg
</code>
<code>
vi /etc/apt/sources.list
</code>
* paste:
<code>
deb [signed-by=/etc/apt/trusted.gpg.d/kitrepo-archive.gpg] https://repo.data.kit.edu//ubuntu/20.04 ./
deb [signed-by=/etc/apt/trusted.gpg.d/kitrepo-archive.gpg] https://repo.data.kit.edu//ubuntu/focal ./
</code>
* save and exit, and do the followinfg command:
<code>
apt-get update
apt-get install oidc-agent
</code>
* to configure the token edit ` vi .bashrc` and set:
<code>
export OIDC_AGENT="sentinel-wlcg"
export REFRESH_TOKEN="eyJhbGc..."
export IAM_CLIENT_SECRET="esLMo..."
export IAM_CLIENT_ID="2a05b..."
export IAM_SERVER=https://iam.cloud.infn.it/
echo "CLOUD storage setup: ${OIDC_AGENT}"
eval `oidc-agent`

oidc-gen --client-id $IAM_CLIENT_ID --client-secret $IAM_CLIENT_SECRET --rt $REFRESH_TOKEN --manual --issuer $IAM_SERVER --pw-cmd="echo pwd" \
--redirect-uri="edu.kit.data.oidc-agent:/redirect http://localhost:29135 http://localhost:8080 http://localhost:4242" --scope \
"openid email wlcg wlcg.groups profile offline_access" $OIDC_AGENT

</code>
then relogin...
