#
# file modify with the path of the daq
#

cd ../../online/
source setup.sh
cd -

export REFRESH_TOKEN="eyJhbGciOiJub25lIn0.eyJqdGkiOiIxMDU2NDFhZS0zODlhLTQ3NWYtYTgyYi1jN2FmNjk0NjE1YTcifQ."
export IAM_CLIENT_SECRET="APABvAtqWkRUH3GQfLiTJzBGiqFpOV7KMmdZtLOtxZgTo6QrvWYI-8ZAYAfHiavFst5jmuKQe-ffofr4Au0eJAg"
export IAM_CLIENT_ID="4b53b391-e7a0-42bb-be5d-a6109c1ae4c5"
export IAM_SERVER=https://iam.cloud.infn.it/
unset OIDC_SOCK; unset OIDCD_PID; eval `oidc-keychain`

#end
