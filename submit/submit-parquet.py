import os, sys
import subprocess
import uproot
import awkward as ak

from coffea import processor, util
from coffea.nanoevents import NanoAODSchema

#Import processor
from boostedhiggs import ParQuetProc

from distributed import Client
from lpcjobqueue import LPCCondorCluster

from dask.distributed import performance_report

#See how long this script takes
from datetime import datetime
import time
tstart = time.time()

cluster = LPCCondorCluster(
    shared_temp_directory="/tmp",
    transfer_input_files=["boostedhiggs"],
    ship_env=True,
    memory="2GB"
)

year = sys.argv[1]
tag = "None"
process_list = ['HtoBB'] #,'HToBB'] #Sample to ignore processing for now

out_path = "output/parquet/{}/{}/".format(tag,year)
os.system('mkdir -p  %s' %out_path)

cluster.adapt(minimum=1, maximum=250)
with Client(cluster) as client:
    
    print(datetime.now())
    print("Waiting for at least one worker...")  # noqa
    client.wait_for_workers(1)
    print(datetime.now())

    with performance_report(filename="dask-report.html"):
        
        #Input PF nano for the year
        infiles = subprocess.getoutput("ls data/infiles/{}/{}_*.json".format(year, year)).split()
    
        for this_file in infiles:
            index = ''.join(this_file.split("_")[1:]).split(".json")[0]
            
            if index in process_list:
                print("Start processing: {}.".format(index))
                print(datetime.now())

                uproot.open.defaults["xrootd_handler"] = uproot.source.xrootd.MultithreadedXRootDSource
                #RUN MAIN PROCESSOR
                p = ParQuetProc(year='2017',
                                jet_arbitration='T_bvc',
                                systematics=False,
                                output_location='./output/parquet/')

                count_total = processor.run_uproot_job(
                    this_file,
                    treename="Events",
                    processor_instance=p,
                    executor=processor.dask_executor,
                    executor_args={
                        "client": client,
                        "skipbadfiles": 1,
                        "schema": processor.NanoAODSchema,
                        "treereduction": 2,
                    },
                    chunksize=50000,
                    maxchunks=1,
                )
            
                #Save output files
                util.save(count_total, outfile)
                print("saved " + outfile)
                print(datetime.now())
            else: pass

elapsed = time.time() - tstart
print("Total time: %.1f seconds"%elapsed)