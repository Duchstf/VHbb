'''
To submit processing jobs, do:

./shell coffeateam/coffea-dask:0.7.21-fastjet-3.4.0.1-g6238ea8

And then

python submit/submit-test.py 2017 > dask.out 2>&1
'''

from coffea import util, processor
from coffea.nanoevents import NanoEventsFactory, NanoAODSchema
import awkward as ak
import os,sys

# Add path so the script sees the modules in parent directory
sys.path.append('/srv')

#Import processor
from boostedhiggs import VHbbProcessorV1
import time
tstart = time.time()

year = '2017'
tag = "vhbb_official_v1"

fileset = {
    "ZH_HToBB_ZToQQ": [
        "root://cmsxrootd.fnal.gov//store/user/lpcpfnano/cmantill/v2_3/2017/HToBB/ZH_HToBB_ZToQQ_M-125_TuneCP5_13TeV-powheg-pythia8/ZH_HToBB_ZToQQ/230217_201213/0000/nano_mc2017_1-1.root"
         ],
}

out_path = "output/coffea/{}/test/".format(tag)
outfile = out_path + '{}_dask_{}.coffea'.format(year, 'ZHTest')
os.system('mkdir -p  %s' %out_path)

p = VHbbProcessorV1(year=year, jet_arbitration='T_bvc' , systematics=True)

output = processor.run_uproot_job(
    fileset,
    treename="Events",
    processor_instance=p,
    executor=processor.iterative_executor,
    executor_args={'schema': NanoAODSchema,'workers': 4},
    chunksize=10000,
    maxchunks=2,
)

#Save output files
util.save(output, outfile)
print("saved " + outfile)

elapsed = time.time() - tstart
print("Total time: %.1f seconds"%elapsed)
                