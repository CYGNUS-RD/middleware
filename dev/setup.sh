#
# file modify with the path of the daq
#


echo "MIDAS setup"
cd ../../online/
source setup.sh
cd -

HOSTNAME=`uname -a | awk '{print $2}'`
# LNF
if [[ $HOSTNAME == "cygno-daq-labe" ]]; then
    echo "Site LNF configured"
elif [[ $HOSTNAME == "RK018155" ]]; then 
    echo "Site LNGS configured"
# LNGS
else
    echo "WARNING: no site configured..."
fi
export REFRESH_TOKEN="eyJhbGciOiJub25lIn0.eyJqdGkiOiIxMDU2NDFhZS0zODlhLTQ3NWYtYTgyYi1jN2FmNjk0NjE1YTcifQ."
export IAM_CLIENT_SECRET="APABvAtqWkRUH3GQfLiTJzBGiqFpOV7KMmdZtLOtxZgTo6QrvWYI-8ZAYAfHiavFst5jmuKQe-ffofr4Au0eJAg"
export IAM_CLIENT_ID="4b53b391-e7a0-42bb-be5d-a6109c1ae4c5"
export IAM_SERVER=https://iam.cloud.infn.it/
unset OIDC_SOCK; unset OIDCD_PID; eval `oidc-keychain`
oidc-gen --client-id $IAM_CLIENT_ID --client-secret $IAM_CLIENT_SECRET --rt $REFRESH_TOKEN --manual --issuer $IAM_SERVER --pw-cmd="echo pwd"  --scope "openid email wlcg wlcg.groups profile offline_access" infncloud-wlcg

echo "ALL DONE"



#end
