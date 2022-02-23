#
# file modify with the path of the daq
#
export DAQ_IN_DIR=/home/cygno/DAQ/online
#
export MIDAS_EXPTAB=$DAQ_IN_DIR/exptab
export MIDAS_EXPT_NAME=CYGNUS_RD

export MYDRIVER_DIR=$DAQ_IN_DIR/mydrivers

export CAENVME=$CAENSYS/CAENVMELib-2.50
export CAENVME_INCDIR=$CAENVME/include
export CAENVME_LIBDIR=$CAENVME/lib/x64

export CAENHV=$CAENSYS/CAENHVWrapper-5.82
export CAENHV_INCDIR=$CAENHV/include
export CAENHV_LIBDIR=$CAENHV/lib/x64

export ETHERNET_INCDIR=$MYDRIVER_DIR/ethernet
export CAMERA_INCDIR=/usr/local/dcamsdk4/inc
export CAMERA_LIBDIR=/usr/local/lib

export LD_LIBRARY_PATH=.:$LD_LIBRARY_PATH

source /home/cygno/root/root_install/bin/thisroot.sh
export REFRESH_TOKEN="eyJhbGciOiJub25lIn0.eyJqdGkiOiI0NzY2YjhlYS1jZjg2LTRjNTEtYmZkYy1hMDRmMDE2YmUyMzQifQ."
export IAM_CLIENT_SECRET="AKlCP9WI6O4R1F9pXVD1enGdZQPYPuAYGsbvggCosVpRABqHis50qQEiScDYazYsdQkKkc7Dc-d060DmmKe9kTQ"
export IAM_CLIENT_ID="18b94299-49fd-4230-8ddc-474b209b2693"
export IAM_SERVER=https://iam.cloud.infn.it/
unset OIDC_SOCK; unset OIDCD_PID; eval `oidc-keychain`
oidc-gen --client-id $IAM_CLIENT_ID --client-secret $IAM_CLIENT_SECRET --rt $REFRESH_TOKEN --manual --issuer $IAM_SERVER --pw-cmd="echo pwd" infncloud-wlcg

export PATH=$PATH:/home/cygno/.local/bin/

#end
