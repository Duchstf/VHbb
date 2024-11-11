voms-proxy-init --voms cms --valid 192:00
source /cvmfs/cms.cern.ch/rucio/setup-py3.sh
export RUCIO_ACCOUNT=duhoang

cut -f 1 datasets_all.txt | while read file; do
    rucio add-rule cms:$file 1 T1_US_FNAL_Disk --lifetime 2600000 --activity 'User AutoApprove' --ask-approval
done
