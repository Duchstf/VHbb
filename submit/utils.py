import json
import os
import subprocess
import uproot
from datetime import datetime

from coffea import processor, util
from coffea.nanoevents import NanoAODSchema

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



