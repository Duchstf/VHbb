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
qcd_WP = 0.0741
mass_range = [40., 68., 110., 201.]

theory_syst_samples = ['VV','VBFDipoleRecoilOn','ggF','ttH', 'WH','ZH']
muonCR_samples = ['QCD', 'singlet', 'ttbar', 'WLNu', "muondata"]

def make_hist_TheorySyst(year, fout):
    '''
    add processed theory systematics to signal_out_path
    '''

    print("Processing Theory Systematics") 
    processed_theory_dir = f'/uscms_data/d3/dhoang/VH_analysis/CMSSW_10_2_13/src/VHbb/output/vhbb_theory_systematics/{year}'

    for sample in theory_syst_samples:
        processed_sample = f'{processed_theory_dir}/{sample}.root'
        theory_file = uproot3.open(processed_sample)

        # List the contents of the source file
        source_keys = theory_file.keys()

        # Iterate through each key in the source file and copy the object to the destination file
        for key in source_keys:
            obj = theory_file[key]
            obj_name = obj.name

            # Check if the object already exists in the destination file
            if obj_name in fout:
                print(f"Object {obj_name} already exists in the destination file. Skipping...")
            else:
                print(f"Copying {obj_name} to the destination file...")
                fout[obj_name] = obj


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

    qcdthr = qcd_WP
    print(f'QCD 2 {year} Threshold: ', qcdthr)

    muonCR_pickle_path = '{}/{}.pkl'.format(year, 'muonCR')
    muonCR_out_path = '{}/muonCRregion.root'.format(year)

    #Make the hists for signal region and muon CR
    make_hists_muonCR(year, bbthr, muonCR_pickle_path, muonCR_out_path)
    
    return

if __name__ == "__main__":
    main()
