"""
Make the input files from the datasets files for processing.
All the files are used from stock nano
Except for ones in custom_list

python make_infiles.py
"""

custom_list = ['VBFDipoleRecoilOn']

import os
import json
import subprocess, sys

with open('../files/pmap.json', 'r') as f: pmap = json.load(f)

for year in ['2016APV']:

    with open(f'nano_list/datasets_{year}.json', 'r') as f: datasets = json.load(f)

    for k, val in pmap.items():

        # one infile per pmap key
        if k in custom_list: continue

        outfilename = f'infiles/{year}/{year}_{k}.json'
        filesets = {}
        for v in val:

            if 'data' in k:
                if year == '2016APV' and not ('2016' in v and 'HIPM' in v): continue
                elif year == "2016" and "HIPM" in v: continue
                elif year not in v and year != '2016APV': continue
               

            filesets[v] = []
            for d in datasets[v]:
                longstring = os.popen("dasgoclient --query=\"file dataset="+d+"\"").read()
                files_no_redirector = longstring.split('\n')

                if ('ttbar' in k) or ('data' in k): filesets[v] += ["root://cmsxrootd-site.fnal.gov//store/test/xrootd/T1_US_FNAL" + f for f in files_no_redirector if len(f) > 0]
                else: filesets[v] += ["root://cmsxrootd-site.fnal.gov/" + f for f in files_no_redirector if len(f) > 0]

            print(v, len(filesets[v]))
           
        with open(outfilename, 'w') as outfile: json.dump(filesets, outfile)