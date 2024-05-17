#!/bin/bash
echo "Starting job on " `date` #Date/time of start of job
echo "Running on: `uname -a`" #Condor job is running on this node
echo "System software: `cat /etc/redhat-release`" #Operating System on that node

CMSSW_VERSION=CMSSW_11_3_4

#bring in the tarball you created before with caches and large files excluded:
source /cvmfs/cms.cern.ch/cmsset_default.sh 
xrdcp -s root://cmseos.fnal.gov//store/user/dhoang/environment/$CMSSW_VERSION.tar.gz .
tar -xf $CMSSW_VERSION.tar.gz
rm $CMSSW_VERSION.tar.gz
cd $CMSSW_VERSION/src/
scramv1 b ProjectRename # this handles linking the already compiled code - do NOT recompile
eval `scramv1 runtime -sh` # cmsenv is an alias not on the workers
echo $CMSSW_BASE "is the CMSSW we have on the local worker node"
cd ${_CONDOR_SCRATCH_DIR}

# My job
echo "Arguments passed to the job: "
echo $1 #pt 
echo $2 #rho
echo $3
echo $4

eosout=$3
index=$4

xrdfs root://cmseos.fnal.gov/ mkdir -p $eosout/

python compare.py --pt=$1 --rho=$2 --ntoys=100 --index=$4

dirs=`ls | grep pt$1rho$2_vs_`
for d in $dirs;
do
    #move output to eos
    xrdfs root://cmseos.fnal.gov/ mkdir $eosout/${d}_$index
    xrdcp -rf $d root://cmseos.fnal.gov/$eosout/${d}_$index
done