'''
Run within singularity image
'''

from coffea import util, processor
from coffea.nanoevents import NanoEventsFactory, NanoAODSchema
import awkward as ak
import os,sys

# Add path so the script sees the modules in parent directory
sys.path.append('/srv')

fileset = {
    "QCD_HT1000to1500": [
        "root://cmseos.fnal.gov//store/user/lpcpfnano/cmantill/v2_3/2017/QCD/QCD_HT1000to1500_TuneCP5_PSWeights_13TeV-madgraph-pythia8/QCD_HT1000to1500/220808_164439/0000/nano_mc2017_1-1.root"
    ],
}

#autoreload forces the kernel to reload the processor to include any new changes
from boostedhiggs import ParQuetProc

import time
tstart = time.time()

p = ParQuetProc(year='2017', jet_arbitration='T_bvc' , systematics=False, output_location='./output/parquet/test')

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

