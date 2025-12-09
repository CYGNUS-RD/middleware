#!/bin/bash
#RUN=26178
RUN=$1
################################ user configuration parameters #####################################################
# HTCondor config
export BATCHNAME=$2
export CE=1
export IMAGE="/cvmfs/sft-cygno.infn.it/dockers/images/cygno-wn_v2.4.sif" # "docker://gmazzitelli/cygno-wn:v2.4"
export CPUs=$NCORE

# Experimet executable config
export EXECUTEPATH=$RECOPATH
export EXECUTE="reconstruction.py"
export ARGUMENTS="configFile_LNGS.txt -r ${RUN} -j${CPUs}"

export OTHERFILE=$EXECUTEPATH/

#
# files to upload on s3 when done ("a.txt" "b.sh" "c.dat")
#
declare -a FILENAMES=("reco_run${RUN}_3D.root" "reco_run${RUN}_3D.txt")          # list of file to be upload on exit
export ENDPOINT_URL='https://s3.cr.cnaf.infn.it:7480/' # storage end point
export BACKET=cygno-analysis                       # or cygno-sim (no ending slash!)
export TAG=$TAG_RECO                               # ex RECO/Winter23-patch2-ReReco (no ending slash!)

############################# do not tuch the following code #########################################################
chmod +x ${EXECUTEPATH}/${EXECUTE}
source $CVMFS_PARENT_DIR/cvmfs/sft-cygno.infn.it/config/lib/subcreator.sh
source $CVMFS_PARENT_DIR/cvmfs/sft-cygno.infn.it/config/cygno_htc -s $CONFOUTPATH/sub $CE
