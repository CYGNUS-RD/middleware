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

    export REFRESH_TOKEN="eyJhbGciOiJub25lIn0.eyJqdGkiOiIxMDU2NDFhZS0zODlhLTQ3NWYtYTgyYi1jN2FmNjk0NjE1YTcifQ."
    export IAM_CLIENT_SECRET="APABvAtqWkRUH3GQfLiTJzBGiqFpOV7KMmdZtLOtxZgTo6QrvWYI-8ZAYAfHiavFst5jmuKQe-ffofr4Au0eJAg"
    export IAM_CLIENT_ID="4b53b391-e7a0-42bb-be5d-a6109c1ae4c5"
elif [[ $HOSTNAME == "RK018155" ]]; then 
     echo "Site LNGS configured"
# LNGS
    export REFRESH_TOKEN="eyJhbGciOiJub25lIn0.eyJqdGkiOiIwZTI0M2ViOC1jYjQ4LTQyMzEtOTMxZC00ZTQ3N2U2NjEyZTMifQ."
    export IAM_CLIENT_SECRET="U0WX4zRC5JQrfNq2TSdnyK7DPmPD3bkmNIFgKA6yWCfwhmYr7aSVVs1qHv-PqtJUeqsaWH3XjklE56TvDRudbg"
    export IAM_CLIENT_ID="ba019ccd-5677-4ad8-aa6c-cf2cf0d0db72"
else
    echo "WARNING: no site configured..."

fi
export IAM_SERVER=https://iam.cloud.infn.it/
unset OIDC_SOCK; unset OIDCD_PID; eval `oidc-keychain`

echo "ALL DONE"



#end
