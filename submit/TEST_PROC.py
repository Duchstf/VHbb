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
    # "WminusH_HToBB_WToQQ": ["root://cmsxrootd-site.fnal.gov//store/mc/RunIISummer20UL18NanoAODv9/WminusH_HToBB_WToQQ_M-125_TuneCP5_13TeV-powheg-pythia8/NANOAODSIM/106X_upgrade2018_realistic_v16_L1v1-v1/70000/BA771CBA-53E3-C74E-A67A-C8B248353201.root"]
    "TEST": [
         "root://cmsxrootd-site.fnal.gov//store/mc/RunIISummer20UL18NanoAODv9/WWTo1L1Nu2Q_4f_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/106X_upgrade2018_realistic_v16_L1v1-v1/60000/E9F0F284-9256-2F42-A191-2AB133595762.root"]
}

#autoreload forces the kernel to reload the processor to include any new changes
from boostedhiggs import VHBB_MuonCR_Processor as vhbb_processor

import time
tstart = time.time()

p = vhbb_processor(year='2016', jet_arbitration='T_bvq', systematics=False)

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

