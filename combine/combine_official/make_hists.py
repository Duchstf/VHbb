#!/usr/bin/python  

'''
Make histograms for different mass bins regions.

python make_hists.py [year]

Example:

python make_hists.py 2017 
'''

import os, sys
import json
import uproot3
from coffea import hist
import pickle

with open('files/lumi.json') as f: lumis = json.load(f)
bb_WPs = { '2016APV_bb1': 0.9883, '2016_bb1': 0.9883, '2017_bb1': 0.9870, '2018_bb1':  0.9880}
qcd_WPs = { '2016APV_qcd2': 0.0541, '2016_qcd2': 0.0882, '2017_qcd2': 0.0541, '2018_qcd2':  0.0741}
mass_range = [40., 68., 110., 201.]

#Same in make_cards.py
samples = ['QCD','VV','Wjets', 'Zjets',
            'VBFDipoleRecoilOn','ggF','ttH', 'WH','ZH',
            'singlet', 'ttbar',
            'data']

samples_save = [x for x in samples + ['Zjetsbb', 'WjetsQQ'] if x != 'Wjets']
btag_SF_samples = ['Wjets', 'Zjets']

muonCR_samples = ['QCD', 'singlet', 'ttbar', 'WLNu', "muondata"]

def check_missing(pickle_hist):
        
    #Print sample names
    hist_samples = [x.name for x in pickle_hist.identifiers('process')]
    print("Available samples: ", hist_samples)

    missing_items = [item for item in samples if item not in hist_samples]
    if missing_items: raise ValueError(f"Missing items: {missing_items}")
    
    #Save the sample & systematics and massrange here and then load it in make_cards.py
    with open("files/samples.json", "w") as f: json.dump(samples_save, f)
    sys_list = [x.name for x in pickle_hist.identifiers('systematic')]
    with open("files/sys_list.json", "w") as f: json.dump(sys_list, f)
    with open("files/Vmass.json", "w") as f:json.dump(mass_range, f)

def make_hists_signal(year, bbthr, qcdthr, signal_pickle_path, signal_out_path):

    #If file already exists remove it and create a new file
    if os.path.isfile(signal_out_path): os.remove(signal_out_path)
    fout = uproot3.create(signal_out_path)

    if not os.path.isfile(signal_pickle_path): raise FileNotFoundError("You need to link the pickle file (using absolute paths)")

    #Read in the pickle file
    pickle_hist =  pickle.load(open(signal_pickle_path,'rb')).integrate('region','signal').integrate('qcd2', slice(0., qcdthr)).integrate('pt1', slice(450, None), overflow='over')
    check_missing(pickle_hist)

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

def make_hists_muonCR(year, bbthr, muonCR_pickle_path, muonCR_out_path):

    print(f"Making hists in muon CR {year} ...")

    #If file already exists remove it and create a new file
    if os.path.isfile(muonCR_out_path): os.remove(muonCR_out_path)
    fout = uproot3.create(muonCR_out_path)

    if not os.path.isfile(muonCR_pickle_path): raise FileNotFoundError("You need to link the pickle file (using absolute paths)")
    with open("files/muonCRsamples.json", "w") as f:json.dump(muonCR_samples, f) #Save the muonCR samples

    #Read in the pickle file
    h = pickle.load(open(muonCR_pickle_path,'rb')).integrate('region','muoncontrol').sum('genflavor1', overflow='all')

    #Split the muon CR into pass and fail region
    for p in muonCR_samples:
        print('Processing sample: ', p)

        hpass = h.integrate('bb1',int_range=slice(bbthr,1.)).integrate('process',p)
        hfail = h.integrate('bb1',int_range=slice(0.,bbthr)).integrate('process',p)
                
        #No systematics for now
        for s in hfail.identifiers('systematic'):
            fout[f"muonCR_pass_{p}_{s}"] = hist.export1d(hpass.integrate('systematic',s))
            fout[f"muonCR_fail_{p}_{s}"] = hist.export1d(hfail.integrate('systematic',s))

    return

# Main method
def main():

    if len(sys.argv) < 2:
        print("Enter year!")
        return
    
    elif len(sys.argv) > 2:
        print("Incorrect number of arguments")
        return

    #Define the most basic parameters
    year = sys.argv[1]
    
    #Define the score threshold
    bbthr = bb_WPs[f'{year}_bb1']
    print(f'BB1 {year} Threshold: ', bbthr)

    qcdthr = qcd_WPs[f'{year}_qcd2']
    print(f'QCD 2 {year} Threshold: ', qcdthr)
    
    signal_pickle_path = '{}/{}.pkl'.format(year, 'signal')
    signal_out_path = '{}/signalregion.root'.format(year)

    muonCR_pickle_path = '{}/{}.pkl'.format(year, 'muonCR')
    muonCR_out_path = '{}/muonCRregion.root'.format(year)

    #Make the hists for signal region and muon CR
    make_hists_signal(year, bbthr, qcdthr, signal_pickle_path, signal_out_path)
    make_hists_muonCR(year, bbthr, muonCR_pickle_path, muonCR_out_path)
    
    return

if __name__ == "__main__":
    main()
