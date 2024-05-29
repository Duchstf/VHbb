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

# env_extra = [
#     "export XRD_RUNFORKHANDLER=1",
#     f"export X509_USER_PROXY=/uscms/home/dhoang/x509up_u55495",
#     # f'export X509_CERT_DIR={os.environ["X509_CERT_DIR"]}',
# ]

# for cmd in env_extra:
#     os.system(cmd)

fileset = {
    "test": [
         "root://cmsxrootd-site.fnal.gov//store/mc/RunIISummer20UL16NanoAODv9/ZH_HToBB_ZToQQ_M-125_TuneCP5_13TeV-powheg-pythia8/NANOAODSIM/106X_mcRun2_asymptotic_v17-v1/60000/B18E6AAE-DCC4-0D4F-8D5E-1EE098BD7C4F.root"]
}

#autoreload forces the kernel to reload the processor to include any new changes
from boostedhiggs import VHbbProcessorOfficial_TheorySys as vhbb_processor

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

