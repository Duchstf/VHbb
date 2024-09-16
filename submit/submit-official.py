'''
To submit processing jobs, do:

ssh -L 8787:localhost:8787 dhoang@cmslpc325.fnal.gov
grid-proxy-init -valid 10000:00

./shell

And then

python submit/submit-official.py $year > dask.out 2>&1
'''

import os, sys
import subprocess
import uproot
import utils 

from coffea import processor, util
from coffea.nanoevents import NanoAODSchema

# Add path so the script sees the modules in parent directory
sys.path.append('/srv')

#Import processor
from boostedhiggs import VHbbProcessorOfficial as vhbb_processor
tag = "vhbb_official"
syst = True
year = sys.argv[1]
ignore_list = ['muondata','WLNu'] #Sample to ignore processing

from distributed import Client
from lpcjobqueue import LPCCondorCluster
from dask.distributed import performance_report
from dask_jobqueue import HTCondorCluster, SLURMCluster

from datetime import datetime

env_extra = [
    f"export PYTHONPATH=$PYTHONPATH:{os.getcwd()}",
    "export XRD_RUNFORKHANDLER=1",
    f"export X509_USER_PROXY=/uscms/home/dhoang/x509up_u55495"
]

for cmd in env_extra:
    os.system(cmd)

cluster = LPCCondorCluster(
    shared_temp_directory="/tmp",
    transfer_input_files=["boostedhiggs"],
    ship_env=True,
    memory="4GB"
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

        for sample_json in infiles:
            
            #Sample name
            sample_name = ''.join(sample_json.split("_")[1:]).split(".json")[0]
            if sample_name in ignore_list:
                print("{} is in ingore list, skipping ...".format(sample_name))
                continue
            
            output_sample_dir = f'{out_path}{sample_name}'

            #Make a folder according to sample name
            os.system(f'mkdir -p {output_sample_dir}')

            #Create sub-json files that belongs to the samples
            utils.split_sample_json(sample_json, output_sample_dir)

            #Create the processor
            p = vhbb_processor(year=year, jet_arbitration='T_bvq' , systematics=syst)

            #Submit the sample
            utils.submit_sample(output_sample_dir, client, p)
