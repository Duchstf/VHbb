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
    
ParticleNet_WorkingPoints = {
    
    '2016APV_bb':    [0.0, 0.9088, 0.9737, 0.9883],
    '2016APV_cc':    [0.0, 0.9252, 0.9751, 0.9909],
    
    '2016_bb': [0.0, 0.9137, 0.9735, 0.9883],
    '2016_cc': [0.0, 0.9252, 0.9743, 0.9905],
    
    '2017_bb':    [0.0, 0.9105, 0.9714, 0.9870],
    '2017_cc':    [0.0, 0.9347, 0.9765, 0.9909],
    
    '2018_bb':    [0.0, 0.9172, 0.9734, 0.9880],
    '2018_cc':    [0.0, 0.9368, 0.9777, 0.9917]
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
    ddbthr = ParticleNet_WorkingPoints['{}_bb'.format(year)][3]
    ddcthr = ParticleNet_WorkingPoints['{}_cc'.format(year)][1]
    
    print('BB1 Threshold: ', ddbthr)
    print('CC2 Threshold: ', ddcthr)
    
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
    with open("files/samples.json", "w") as f:   #Pickling
        json.dump(samples, f)
    
    #Process each region
    for region in regions:
        
        print('Running for {} in {} region'.format(year, region))
        systematic = 'nomial'
    
        # Jet 2 charm score integral range
        c_int_range = slice(ddcthr, None) if region == 'charm' else slice(0,ddcthr)
        c_overflow = 'over' if region == 'charm' else 'none'
        
        # Read the histogram from the pickle file
        # Integrate over signal region and Jet 2 charm score
        sig = pickle.load(open(pickle_path,'rb')).integrate('region','signal')
        sig = sig.sum('pt1', overflow='all')
        sig = sig.integrate('cc2', c_int_range, overflow=c_overflow)

        #Print names
        # print([x.name for x in sig.integrate('bb1',int_range=slice(ddbthr,1)).sum('msd1').identifiers('process')])
        # print([x.name for x in sig.sum('bb1','msd1','process').identifiers('systematic')])
    
        #Split into Jet 1 score b-tag passing/failing region. 
        for p in samples:
            print('Processing sample: ', p)

            hpass = sig.integrate('bb1',int_range=slice(ddbthr,None), overflow='over').integrate('process',p)
            hfail = sig.integrate('bb1',int_range=slice(0,ddbthr)).integrate('process',p)
        
            for s in hfail.identifiers('systematic'):
                fout["{}_pass_{}_{}".format(region, p, s)] = hist.export1d(hpass.integrate('systematic', s))
                fout["{}_fail_{}_{}".format(region, p, s)] = hist.export1d(hfail.integrate('systematic', s))

    return

if __name__ == "__main__":
    main()
