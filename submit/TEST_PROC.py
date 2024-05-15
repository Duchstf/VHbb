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
    "JetHT_Run2016B_ver1_HIPM": [
          "root://cmsxrootd-site.fnal.gov//store/test/xrootd/T1_US_FNAL/store/data/Run2016F/JetHT/NANOAOD/HIPM_UL2016_MiniAODv2_NanoAODv9-v2/40000/617DDB59-9383-4A4E-A257-CA658B0EE08B.root"]
}

#autoreload forces the kernel to reload the processor to include any new changes
from boostedhiggs import VhbbPNQCDScan as vhbb_processor

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

