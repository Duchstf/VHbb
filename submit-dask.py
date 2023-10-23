import os, sys
import subprocess
import uproot

from coffea import processor, util, hist
from coffea.nanoevents import NanoEventsFactory, NanoAODSchema

#Import processor
from boostedhiggs import ParticleNetMsdProcessor

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
    memory="12GB"
#    image="coffeateam/coffea-dask:0.7.11-fastjet-3.3.4.0rc9-ga05a1f8",
)

year = sys.argv[1]
tag = "pnet_scan_msd_QCD_Oct22_2023"
ignore_list = ['QCDbEnriched', 'QCDBGenFilter', 'VBFHToBBDipoleRecoilOn'] #Sample to ignore processing for now

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
        infiles = subprocess.getoutput("ls data/infiles/{}/{}_*.json".format(year, year)).split()
    
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
                p = ParticleNetMsdProcessor(year=year, jet_arbitration='T_bvc' , systematics=False)
                args = {'savemetrics':True, 'schema':NanoAODSchema}

                output = processor.run_uproot_job(
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
                    #        maxchunks=args.max,
                )

                #Save output files
                util.save(output, outfile)
                print("saved " + outfile)
                print(datetime.now())
