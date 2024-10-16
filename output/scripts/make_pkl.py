#!/usr/bin/python  

"""
Make a pickle file out of the coffea histograms. Like this:

./shell

python make_pkl.py 2017 pnet_scan_msd_Aug4_2023
"""

import os, sys
import subprocess
import json
from coffea import processor, util, hist
import pickle

# Main method
def main():
    
    #Load all the files
    with open('../../files/xsec.json') as f: xs = json.load(f)     
    with open('../../files/pmap.json') as f: pmap = json.load(f)
    with open('../../files/lumi.json') as f: lumis = json.load(f)
    if len(sys.argv) < 3: raise Exception("Enter both year and tag.") # Take in the year and tag

    year = sys.argv[1]
    tag = sys.argv[2]
    hist_name = 'h' #You need to define this manually, usually just keep it as "templates"
            
    indir = "../coffea/{}/{}/".format(tag, year)
    infiles = subprocess.getoutput("ls "+indir+year+"_dask_*.coffea").split()
    outsum = processor.dict_accumulator()

    # Check if pickle exists, remove it if it does
    # Make the output directory
    outdir = '../pickle/{}/{}'.format(tag,year)
    os.system('mkdir -p  %s' %outdir)

    # Templates file is the collection of all processed histogram
    picklename = outdir  + '/h.pkl'
    if os.path.isfile(picklename):
        os.remove(picklename)

    started = 0
    for filename in infiles:

        print("Loading "+filename)
        
        if os.path.isfile(filename):
            out = util.load(filename)

            if started == 0:
                outsum[hist_name] = out[0][hist_name]
                outsum['sumw'] = out[0]['sumw']
                started += 1
            else:
                outsum[hist_name].add(out[0][hist_name])
                outsum['sumw'].add(out[0]['sumw'])

            del out

    scale_lumi = {k: xs[k] * 1000 * lumis[year] / w for k, w in outsum['sumw'].items()} 

    # Scale the output with luminosity
    outsum[hist_name].scale(scale_lumi, 'dataset')
    print(outsum[hist_name].identifiers('dataset'))
    templates = outsum[hist_name].group('dataset', hist.Cat('process', 'Process'), pmap)

    del outsum
    
    # Write the pickle file      
    outfile = open(picklename, 'wb')
    pickle.dump(templates, outfile, protocol=-1)
    outfile.close()

    return

if __name__ == "__main__":

    main()
