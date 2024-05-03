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
    '2016_bb1': 0.9883,
    '2017_bb1': 0.9870,
    '2018_bb1':  0.9880,
}

mass_range = [40., 68., 110., 201.]

#Same in make_cards.py
samples = ['QCD','WH','ZH','VV',
            'Wjets', 'Zjets',
            'VBFDipoleRecoilOn','ggF','ttH',
            'singlet',
            'ttbar',
            'data', #!DATA MISSING FOR EACH YEAR
            ]

#Devide Wjets into unmatched and matched components
samples_save = [x for x in samples + ['Zjetsbb', 'WjetsQQ'] if x != 'Wjets']

btag_SF_samples = ['Wjets', 'Zjets']

QCD2_THRES = 0.0922

def check_missing(pickle_hist):
        
    #Print sample names
    hist_samples = [x.name for x in pickle_hist.identifiers('process')]
    print("Available samples: ", hist_samples)
    print("Checking available samples ... ")
    
    # Find items in samples that are not in hist_samples
    missing_items = [item for item in samples if item not in hist_samples]
    
    # Check if there are any missing items
    if missing_items:
        # Raise an error and include information about the missing items
        raise ValueError(f"Missing items: {missing_items}")
    
    #Save the sample here and then load it in make_cards.py
    with open("files/samples.json", "w") as f:   #Pickling
        json.dump(samples_save, f)
        
    sys_list = [x.name for x in pickle_hist.identifiers('systematic')]
    
    #Save the systematics here
    with open("files/sys_list.json", "w") as f:   #Pickling
        json.dump(sys_list, f)
    
# Main method
def main():

    if len(sys.argv) < 2:
        print("Enter year")
        return
    
    elif len(sys.argv) > 2:
        print("Incorrect number of arguments")
        return

    #Define the most basic parameters
    year = sys.argv[1]
    
    #Define the score threshold
    bbthr = WPs[f'{year}_bb1']
    print(f'BB1 {year} Threshold: ', bbthr)
    
    pickle_path = '{}/{}.pkl'.format(year, 'ParticleNet_msd') #Need to be defined manually
    out_path = '{}/signalregion.root'.format(year)
    
    #If file already exists remove it and create a new file
    if os.path.isfile(out_path): os.remove(out_path)
    fout = uproot3.create(out_path)
    
    #Check if pickle exists     
    if not os.path.isfile(pickle_path):
        raise FileNotFoundError("You need to link the pickle file (using absolute paths)")

    #Read in the pickle file
    pickle_hist =  pickle.load(open(pickle_path,'rb')).integrate('region','signal').integrate('qcd2', slice(0., QCD2_THRES))
    check_missing(pickle_hist)
    
    #Save a list of mass categories to a file to be used in make_cards
    with open("files/Vmass.json", "w") as f:   #Pickling
        json.dump(mass_range, f)

    #Process each region
    for i in range(len(mass_range)-1):

        print('Running for {} in {} mass region'.format(year, i))
        msd2_int_range = slice(mass_range[i], mass_range[i+1])
        sig = pickle_hist.integrate('msd2', msd2_int_range)
        
        #Split into Jet 1 score b-tag passing/failing region. 
        for p in samples:
            print('Processing sample: ', p)
            
            #Just initialize the values
            hpass=None
            hfail=None
            
            if p not in btag_SF_samples:
                
                hpass = sig.integrate('bb1',int_range=slice(bbthr,1.)).sum('genflavor1', overflow='under').integrate('process',p)
                hfail = sig.integrate('bb1',int_range=slice(0.,bbthr)).sum('genflavor1', overflow='under').integrate('process',p)
                          
                for s in hfail.identifiers('systematic'):
                        fout[f"Vmass_{i}_pass_{p}_{s}"] = hist.export1d(hpass.integrate('systematic',s))
                        fout[f"Vmass_{i}_fail_{p}_{s}"] = hist.export1d(hfail.integrate('systematic',s))
                
            elif p == 'Wjets': #Divide Wjets into unmatched and matched
                
                hpass_qq = sig.integrate('bb1',int_range=slice(bbthr,1.)).integrate('genflavor1', int_range=slice(1, None)).integrate('process',p)
                hfail_qq = sig.integrate('bb1',int_range=slice(0.,bbthr)).integrate('genflavor1', int_range=slice(1, None)).integrate('process',p)
                
                for s in hpass_qq.identifiers('systematic'):
                    
                    fout[f"Vmass_{i}_pass_{p + 'QQ'}_{s}"] = hist.export1d(hpass_qq.integrate('systematic',s))
                    fout[f"Vmass_{i}_fail_{p + 'QQ'}_{s}"] = hist.export1d(hfail_qq.integrate('systematic',s))
                
            else: #Divide Zjets into Z(qq) and Z(bb)
                
                hpass = sig.integrate('genflavor1', int_range=slice(1,3)).integrate('bb1',int_range=slice(bbthr,1.)).integrate('process',p)
                hfail = sig.integrate('genflavor1', int_range=slice(1,3)).integrate('bb1',int_range=slice(0.,bbthr)).integrate('process',p)
                
                hpass_bb = sig.integrate('genflavor1', int_range=slice(3,4)).integrate('bb1',int_range=slice(bbthr,1.)).integrate('process',p)
                hfail_bb = sig.integrate('genflavor1', int_range=slice(3,4)).integrate('bb1',int_range=slice(0.,bbthr)).integrate('process',p)
                
                for s in hfail.identifiers('systematic'):
                    fout[f"Vmass_{i}_pass_{p}_{s}"] = hist.export1d(hpass.integrate('systematic',s))
                    fout[f"Vmass_{i}_fail_{p}_{s}"] = hist.export1d(hfail.integrate('systematic',s))
                        
                    fout[f"Vmass_{i}_pass_{p + 'bb'}_{s}"] = hist.export1d(hpass_bb.integrate('systematic',s))
                    fout[f"Vmass_{i}_fail_{p + 'bb'}_{s}"] = hist.export1d(hfail_bb.integrate('systematic',s))

    
    return

if __name__ == "__main__":
    main()
