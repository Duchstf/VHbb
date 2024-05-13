"""
Make the input files from the datasets files for processing.
All the files are used from stock nano
Except for ones in custom_list

python make_infiles.py
"""

custom_list = ['VBFHToBB_DipoleRecoilOn']

import os
import json
import subprocess, sys

with open('../files/pmap.json', 'r') as f: pmap = json.load(f)

for year in ['2016','2016APV', '2017', '2018']:

    with open(f'nano_list/datasets_{year}.json', 'r') as f: datasets = json.load(f)

    for k, val in pmap.items():

        # one infile per pmap key
        outfilename = f'infiles/{year}/{year}_{k}.json'

        filesets = {}
        for v in val:

            if v in custom_list: continue

            if 'data' in k:
                if year == '2016APV' and not ('2016' in v and 'HIPM' in v): continue
                elif year not in v: continue
                elif year == "2016" and "HIPM" in v: continue

            filesets[v] = []
            for d in datasets[v]:
                longstring = os.popen("dasgoclient --query=\"file dataset="+d+"\"").read()
                files_no_redirector = longstring.split('\n')
                filesets[v] += ["root://cmsxrootd.fnal.gov//store/test/xrootd/T1_US_FNAL" + f for f in files_no_redirector if len(f) > 0]

            print(v, len(filesets[v]))
           
        with open(outfilename, 'w') as outfile: json.dump(filesets, outfile)