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
    "QCD": [
         "root://cmsxrootd-site.fnal.gov//store/mc/RunIISummer20UL16NanoAODv9/QCD_HT300to500_TuneCP5_PSWeights_13TeV-madgraph-pythia8/NANOAODSIM/106X_mcRun2_asymptotic_v17-v1/260000/527D7EFD-7081-6B42-8A3B-F3ED40C989C3.root"]
}

#autoreload forces the kernel to reload the processor to include any new changes
from boostedhiggs import DDT as vhbb_processor

import time
tstart = time.time()

p = vhbb_processor(year='2016', jet_arbitration='T_bvq')

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

