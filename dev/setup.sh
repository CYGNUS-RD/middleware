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

#end
