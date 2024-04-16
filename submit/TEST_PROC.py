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
    "ZJetsToQQ_HT-600to800": [
         "root://cmsxrootd.fnal.gov//store/user/lpcpfnano/rkansal/v2_3/2017/ZJetsToQQ/ZJetsToQQ_HT-600to800_TuneCP5_13TeV-madgraphMLM-pythia8/ZJetsToQQ_HT-600to800/220705_160538/0000/nano_mc2017_39.root"
    ],
}

#autoreload forces the kernel to reload the processor to include any new changes
from boostedhiggs import VHbbProcessorV10

import time
tstart = time.time()

p = VHbbProcessorV10(year='2017', jet_arbitration='T_bvc')

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

