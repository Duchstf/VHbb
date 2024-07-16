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
    "test": [
         "root://cmsxrootd-site.fnal.gov//store/mc/RunIISummer20UL18NanoAODv9/QCD_HT100to200_TuneCP5_PSWeights_13TeV-madgraph-pythia8/NANOAODSIM/106X_upgrade2018_realistic_v16_L1v1-v1/2520000/C9C073BD-47D3-8F43-A809-EDA7FFBF176E.root"]
}

#autoreload forces the kernel to reload the processor to include any new changes
from boostedhiggs import VHBB_WTagCR as vhbb_processor

import time
tstart = time.time()

p = vhbb_processor(year='2018', jet_arbitration='T_bvq')

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

