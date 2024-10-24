'''
To submit processing jobs, do:

ssh -L 8787:localhost:8787 dhoang@cmslpc325.fnal.gov
grid-proxy-init -valid 10000:00

./shell

And then

python submit/submit-2DMass.py $year > dask.out 2>&1
'''

import os, sys
import subprocess
import uproot

from coffea import processor, util
from coffea.nanoevents import NanoAODSchema

# Add path so the script sees the modules in parent directory
sys.path.append('/srv')

#Import processor
from boostedhiggs import VHbbProcessor2DMass as vhbb_processor
tag = "vhbb_2dmass"
syst = False
year = sys.argv[1]
ignore_list = ['muondata', 'WW_NLO', 'WZ_NLO', 'ZZ_NLO'] #Sample to ignore processing

from distributed import Client
from lpcjobqueue import LPCCondorCluster
from dask.distributed import performance_report
from dask_jobqueue import HTCondorCluster, SLURMCluster

from datetime import datetime

env_extra = [
    f"export PYTHONPATH=$PYTHONPATH:{os.getcwd()}",
]

cluster = LPCCondorCluster(
    shared_temp_directory="/tmp",
    transfer_input_files=["boostedhiggs"],
    ship_env=True,
    memory="6GB"
#    image="coffeateam/coffea-dask:0.7.11-fastjet-3.3.4.0rc9-ga05a1f8",
)

out_path = "output/coffea/{}/{}/".format(tag,year)
os.system('mkdir -p  %s' %out_path)

cluster.adapt(minimum=1, maximum=250)
with Client(cluster) as client:
    
    print(datetime.now())
    print("Waiting for at least one worker...")  # noqa
    client.wait_for_workers(1)
    print(datetime.now())

    with performance_report(filename="dask-report.html"):
        
        #Input PF nano for the year
        infiles = subprocess.getoutput("ls datasets/infiles/{}/{}_*.json".format(year, year)).split()
    
        for this_file in infiles:
            index = ''.join(this_file.split("_")[1:]).split(".json")[0]
            outfile = out_path + '{}_dask_{}.coffea'.format(year, index)
            
            if index in ignore_list:
                print("{} is in ingore list, skipping ...".format(index))
                continue
    
            if os.path.isfile(outfile):
                print("File " + outfile + " already exists. Skipping.")
                continue 
            
            else:
                print("Begin running " + outfile)
                print(datetime.now())

                uproot.open.defaults["xrootd_handler"] = uproot.source.xrootd.MultithreadedXRootDSource

                #RUN MAIN PROCESSOR
                p = vhbb_processor(year=year, jet_arbitration='T_bvq' , systematics=syst)
                args = {'savemetrics':True, 'schema':NanoAODSchema}

                #Safe to skip bad files for MC, not safe for data
                skipBadFiles = 0 if 'data' in index else 1
                output = processor.run_uproot_job(
                    this_file,
                    treename="Events",
                    processor_instance=p,
                    executor=processor.dask_executor,
                    executor_args={
                        "client": client,
                        "schema": processor.NanoAODSchema,
                        "treereduction": 2,
                        "savemetrics": True,
                        "skipbadfiles": skipBadFiles,
                    },
                    chunksize=50000,
                )

                #Save output files
                util.save(output, outfile)
                print("saved " + outfile)
                print(datetime.now())
