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

with open('files/lumi.json') as f:
    lumis = json.load(f)
    
WPs = {
    
    '2016APV_bb1': 0.9883,
    '2016APV_cc2': 0.9909,
    
    '2016_bb1': 0.9883,
    '2016_cc2': 0.9883,
    
    '2017_bb1': 0.9918,
    '2017_cc2': 0.0,
    
    '2018_bb1':  0.9880,
    '2018_cc2':  0.9917
}

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
    
    #Define the score threshold
    bbthr = WPs[f'{year}_bb1']
    ccthr = WPs[f'{year}_cc2']
    
    print(f'BB1 {year} Threshold: ', bbthr)
    print(f'CC2 {year} Threshold: ', ccthr)
    
    pickle_path = '{}/{}.pkl'.format(year, 'ParticleNet_msd') #Need to be defined manually
    out_path = '{}/signalregion.root'.format(year)
    
    #If file already exists remove it and create a new file
    if os.path.isfile(out_path):
        os.remove(out_path)
    fout = uproot3.create(out_path)
    
    #Check if pickle exists     
    if not os.path.isfile(pickle_path):
        print("You need to link the pickle file (using absolute paths)")
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
    with open("files/samples.json", "w") as f:   #Pickling
        json.dump(samples, f)
    
    #Process each region
    for region in regions:
    
        print('Running for {} in {} region'.format(year, region))
    
        # Jet 2 charm score integral range
        c_int_range = slice(ccthr,1) if region == 'charm' else slice(0,ccthr)
        
        # Read the histogram from the pickle file
        # Integrate over signal region and Jet 2 charm score
        sig = pickle.load(open(pickle_path,'rb')).integrate('region','signal').integrate('systematic', 'nominal').integrate('cc2',int_range=c_int_range)

        #Print sample names
        hist_samples = [x.name for x in sig.integrate('bb1',int_range=slice(bbthr,1)).sum('msd1').identifiers('process')]
        print("Available samples: ", hist_samples)
        assert(all(item in hist_samples for item in samples))
    
        #Split into Jet 1 score b-tag passing/failing region. 
        for p in samples:
            print('Processing sample: ', p)

            hpass = sig.integrate('bb1',int_range=slice(bbthr,1)).integrate('process',p)
            hfail = sig.integrate('bb1',int_range=slice(0,bbthr)).integrate('process',p)

            fout["{}_pass_{}_nominal".format(region, p)] = hist.export1d(hpass)
            fout["{}_fail_{}_nominal".format(region, p)] = hist.export1d(hfail)

    return

if __name__ == "__main__":
    main()
