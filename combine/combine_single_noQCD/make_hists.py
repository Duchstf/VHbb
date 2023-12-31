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
ddbthr = 0.987
ddcthr = 0.9347

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
    
    #TODO: Current VBF sample is with DipoleRecoil Off, Jennet is generating a new sample with Dipole Recoil On. 
    #TODO: Doesn't matter if using Zjets or ZjetsHT (only the DY samples are different). 
    #TODO: ttbarboosted for higher statistics.
    #TODO: Don't need EWK V

    #! USE THE EXACT SAME SAMPLE IN make_cards.py
    samples = ['data',
            'QCD',
            'WH','ZH',
            'VV',
            'Wjets', 'Zjets',
            'VBFDipoleRecoilOff', #Double checking this.
            'ggF', 
            'singlet',
            'ttH',
            'ttbarBoosted']
    
    #Save the sample here and then load it in make_cards.py
    with open("samples.json", "w") as f:   #Pickling
        json.dump(samples, f)
    
    #Process each region
    for region in regions:
        
        print('Running for {} in {} region'.format(year, region))
    
        # Jet 2 charm score integral range
        c_int_range = slice(ddcthr, None) if region == 'charm' else slice(0,ddcthr)
        c_overflow = 'over' if region == 'charm' else 'none'
        
        # Read the histogram from the pickle file
        # Integrate over signal region and Jet 2 charm score
        sig_0 = pickle.load(open(pickle_path,'rb')).integrate('region','signal').sum('qcd2','qq2','bb2','genflavor2', overflow='all')
        sig = sig_0.integrate('cc2', c_int_range, overflow=c_overflow)
        
        #Print sample names
        #print([x.name for x in sig.integrate('bb1',int_range=slice(ddbthr,1)).sum('msd1').identifiers('process')])
    
        #Split into Jet 1 score b-tag passing/failing region. 
        for p in samples:
            print('Processing sample: ', p)
            
            hpass = sig.integrate('bb1',int_range=slice(ddbthr,None), overflow="over").integrate('process',p)
            hfail = sig.integrate('bb1',int_range=slice(0,ddbthr)).integrate('process',p)
            
            # print("PASS: ", hpass.sum('msd1').integrate(,overflow='under').values()[()])
            # print("FAIL: ", hfail.sum('msd1').integrate('genflavor2',overflow='under').values()[()])

            fout["{}_pass_{}_nominal".format(region, p)] = hist.export1d(hpass)
            fout["{}_fail_{}_nominal".format(region, p)] = hist.export1d(hfail)

   
    return

if __name__ == "__main__":
    main()
