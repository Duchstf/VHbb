#!/usr/bin/python  

'''
Make histograms for charm and light regions.

python make_hists.py [year]

Example:

python make_hists.py 2017 
'''

import os, sys
import json
import uproot3
from coffea import hist
import pickle

with open('lumi.json') as f:
    lumis = json.load(f)

#Define the score threshold
ddbthr = 0.72
ddcthr = 0.15

# Main method
def main():

    if len(sys.argv) < 2:
        print("Enter year")
        return
    
    elif len(sys.argv) > 2:
        print("Incorrect number of arguments")
        return

    year = sys.argv[1]
    regions = ['charm', 'light']
    
    pickle_path = '{}/{}.pkl'.format(year, 'ParticleNet_msd') #Need to be defined manually
    out_path = '{}/signalregion.root'.format(year)
    
    #If file already exists remove it and create a new file
    if os.path.isfile(out_path):
        os.remove(out_path)
    fout = uproot3.create(out_path)
    
     # Check if pickle exists     
    if not os.path.isfile(pickle_path):
        print("You need to create the pickle")
        return
    
    #TODO: Full sample is ['QCD', 'VBFDipoleRecoilOff', 'WH', 'WW', 'WZ', 'Wjets', 'ZH', 'ZZ', 'Zjets', 'ZjetsHT', 'data', 'ggF', 'singlet', 'ttH', 'ttbar', 'ttbarBoosted']
    
    #TODO: Checking with Cristina about her VBF sample, have to make sure using reoil dipole on. 
    #TODO: DO WE NEED  ZjetsHT? ttbarboosted (I think we discussed switching at some point)
    #TODO: Doesn't matter if using Zjets or ZjetsHT. 
    #TODO: ttbarboosted for higher statistics.
    #TODO: What about EWK V?? Don't need
    #TODO: I really need to double check all the samples

    #! USE THE EXACT SAME SAMPLE IN make_cards.py
    samples = ['data',
            'QCD',
            'WH','ZH',
            'WW', 'WZ', 'ZZ',
            'Wjets', 'Zjets',
            'VBFDipoleRecoilOff', #Double checking this.
            'ggF', 
            'singlet',
            'ttH',
            'ttbarBoosted']
    
    #Process each region
    for region in regions:
        
        print('Running for {} in {} region'.format(year, region))
        #bins = [40,201]
    

    
        # Jet 2 charm score integral range
        c_int_range = slice(ddcthr,1) if region == 'charm' else slice(0,ddcthr)
        
        # Read the histogram from the pickle file
        # Integrate over signal region and Jet 2 charm score
        sig = pickle.load(open(pickle_path,'rb')).integrate('region','signal').integrate('ddc2',int_range=c_int_range)

        # print(dir(sig.integrate('ddb1',int_range=slice(ddbthr,1)).sum('msd1').identifiers('process')))
        # print([x.name for x in sig.integrate('ddb1',int_range=slice(ddbthr,1)).sum('msd1').identifiers('process')])
    
        #Split into Jet 1 score b-tag passing/failing region. 
        for p in samples:
            print('Processing sample: ', p)

            hpass = sig.integrate('ddb1',int_range=slice(ddbthr,1)).integrate('process',p)
            hfail = sig.integrate('ddb1',int_range=slice(0,ddbthr)).integrate('process',p)

            fout["{}_pass_{}_nominal".format(region, p)] = hist.export1d(hpass)
            fout["{}_fail_{}_nominal".format(region, p)] = hist.export1d(hfail)

   
    return

if __name__ == "__main__":
    main()
