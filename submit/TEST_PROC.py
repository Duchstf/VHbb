'''
Run within singularity image

./shell
python submit/TEST_PROC.py
'''

from coffea import util, processor
from coffea.nanoevents import NanoEventsFactory, NanoAODSchema
import awkward as ak
import os,sys

# Add path so the script sees the modules in parent directory
sys.path.append('/srv')

fileset = {
    "QCD_HT300to500": [
         "root://cmsxrootd.fnal.gov//store/user/lpcpfnano/cmantill/v2_3/2017/QCD/QCD_HT300to500_TuneCP5_PSWeights_13TeV-madgraph-pythia8/QCD_HT300to500/220808_164621/0000/nano_mc2017_103.root"
    ],
}

#autoreload forces the kernel to reload the processor to include any new changes
from boostedhiggs import VHbbProcessorOfficial as vhbb_processor

import time
tstart = time.time()

p = vhbb_processor(year='2017', jet_arbitration='T_bvq')

#Run Coffea code using uproot
dummy = processor.run_uproot_job(
    fileset,
    treename="Events",
    processor_instance=p,
    executor=processor.iterative_executor,
    executor_args={'schema': NanoAODSchema,'workers': 4},
    chunksize=10000,
    maxchunks=2,
)

elapsed = time.time() - tstart
print("Total time: %.1f seconds"%elapsed)

