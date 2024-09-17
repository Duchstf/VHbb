import json
import os
import subprocess
import uproot
from datetime import datetime

from coffea import processor, util
from coffea.nanoevents import NanoAODSchema

from lpcjobqueue import LPCCondorCluster
from distributed import Client
from dask.distributed import performance_report

def init_cluster(memory='2GB'):
    return LPCCondorCluster(shared_temp_directory="/tmp", transfer_input_files=["boostedhiggs"], ship_env=True, memory=memory)

def run_env_extra():

    env_extra = [
        f"export PYTHONPATH=$PYTHONPATH:{os.getcwd()}",
        "export XRD_RUNFORKHANDLER=1",
        f"export X509_USER_PROXY=/uscms/home/dhoang/x509up_u55495"
    ]

    for cmd in env_extra: os.system(cmd)


def split_sample_json(sample_json, out_dir):
    """
    Parse the sample json to sub-jsons and then output them in out_dir
    """

    with open(sample_json, 'r') as file: sample_dict = json.load(file)

    for key, value in sample_dict.items():
        filename=f'{out_dir}/{key}.json'
        with open(filename, 'w') as json_file: json.dump({key:value}, json_file)

    return 

def submit_sample(output_sample_dir, client, p):
    """
    Iterate through each json file in output_sample_dir and submit them
    """
    print(f'--------------------------------------')
    print(f'Processing sample: {output_sample_dir}')
    infiles = subprocess.getoutput(f"ls {output_sample_dir}/*.json").split()

    for infile in infiles:
        subsample = infile.split(".json")[0].split('/')[-1]
        sub_outfile = f"{output_sample_dir}/{subsample}.coffea"

        if os.path.isfile(sub_outfile):
            print("File " + sub_outfile + " already exists. Skipping.")
            continue 

        print("Processing subfile: ", infile)
        print("Output file: ", sub_outfile)

        uproot.open.defaults["xrootd_handler"] = uproot.source.xrootd.MultithreadedXRootDSource

        #RUN MAIN PROCESSOR
        args = {'savemetrics':True, 'schema':NanoAODSchema}

        #Safe to skip bad files for MC, not safe for data
        skipBadFiles = 0 if 'data' in subsample else 1
        output = processor.run_uproot_job(
            infile,
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
        util.save(output, sub_outfile)
        print("Saved " + sub_outfile)
        print(datetime.now())


def submit_processor(year, tag, processor, memory, ignore_list=None, target_list=None):

    cluster = init_cluster(memory)
    run_env_extra()

    out_path = f"output/coffea/{tag}/{year}/"
    os.system('mkdir -p  %s' %out_path)

    cluster.adapt(minimum=1, maximum=250)
    with Client(cluster) as client:
        
        print("Waiting for at least one worker...")
        client.wait_for_workers(1)

        with performance_report(filename="dask-report.html"):
            
            #Input PF nano for the year
            infiles = subprocess.getoutput(f"ls datasets/infiles/{year}/{year}_*.json").split()

            for sample_json in infiles:
                
                #Sample name
                sample_name = ''.join(sample_json.split("_")[1:]).split(".json")[0]

                if ignore_list & (sample_name in ignore_list):
                    print("{} is in ingore list, skipping ...".format(sample_name))
                    continue
                
                if target_list & (sample_name not in target_list):
                    print("{} is not in target list, skipping ...".format(sample_name))
                    continue

                output_sample_dir = f'{out_path}{sample_name}'

                #Make a folder according to sample name
                os.system(f'mkdir -p {output_sample_dir}')

                #Create sub-json files that belongs to the samples
                split_sample_json(sample_json, output_sample_dir)

                #Create the processor
                p = processor

                #Submit the sample
                submit_sample(output_sample_dir, client, processor)

