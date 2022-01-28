#!/bin/bash

export REFRESH_TOKEN="eyJhbGciOiJub25lIn0.eyJqdGkiOiI0NzY2YjhlYS1jZjg2LTRjNTEtYmZkYy1hMDRmMDE2YmUyMzQifQ."
export IAM_CLIENT_SECRET="AKlCP9WI6O4R1F9pXVD1enGdZQPYPuAYGsbvggCosVpRABqHis50qQEiScDYazYsdQkKkc7Dc-d060DmmKe9kTQ"
export IAM_CLIENT_ID="18b94299-49fd-4230-8ddc-474b209b2693"
export IAM_SERVER=https://iam.cloud.infn.it/
unset OIDC_SOCK; unset OIDCD_PID; eval `oidc-keychain`
env
# oidc-token infncloug-wlcg