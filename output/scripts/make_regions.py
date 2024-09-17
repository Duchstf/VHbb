"""
Only using this to parse the coffea files, since they became too heavy.
Produce everything in the signalregion.root file

Usage:

python make_regions.py <year>
"""

import os, sys
import subprocess
import json
from coffea import processor, util, hist
import pickle
import numpy as np
import uproot3
import shutil

#Year definitions and tags 
if len(sys.argv) < 2: raise Exception("Enter year.") # Take in the year and tag
year = sys.argv[1]
outdir = '../vhbb_official/{}'.format(year)

#Load all the files
with open('../../files/xsec.json') as f: xs = json.load(f)     
with open('../../files/pmap.json') as f: pmap = json.load(f)
with open('../../files/lumi.json') as f: lumis = json.load(f)

#Working points
bb_WPs = { '2016APV_bb1': 0.9883, '2016_bb1': 0.9883, '2017_bb1': 0.9870, '2018_bb1':  0.9880}

#Define the score threshold
bbthr = bb_WPs[f'{year}_bb1']
qcdthr = 0.0741
mass_range = [40., 68., 110., 201.]

#List the samples
samples = ['QCD',
           'VV', 'VVNLO', 'Wjets', 'Zjets',
           'VBFDipoleRecoilOn','ggF','ttH', 'WH','ZH',
           'singlet', 'ttbar',
           'data']

# samples = ['QCD']
btag_SF_samples = ['Wjets', 'Zjets']
muonCR_samples = ['QCD', 'singlet', 'ttbar', 'WLNu', "muondata"]
samples_save = [x for x in samples + ['Zjetsbb', 'WjetsQQ'] if x != 'Wjets']

def make_template_theory(filenames):
    return

def process_theory(fout, filenames):
    return

def make_template(filenames):

    hist_name = 'h' #You need to define this manually, usually just keep it as "templates"
    outsum = processor.dict_accumulator()

    started = 0

    for filename in filenames:

        print("Loading: ", filename)
        
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
    template = outsum[hist_name].group('dataset', hist.Cat('process', 'Process'), pmap)
    del outsum

    return template

def process(fout, sample, filename):
    """
    Slim each sample coffea file into a root file
    """

    #Make the template for the specific sample
    template = make_template(filename)

    h = template.integrate('region','signal').integrate('qcd2', slice(0., qcdthr)).integrate('pt1', slice(450, None), overflow='over').sum('genflavor2', overflow='under')

    #Make hists for different mass ranges
    for i in range(len(mass_range)-1):
        print('Running for {} in {} mass region'.format(year, i))
        msd2_int_range = slice(mass_range[i], mass_range[i+1])
        sig = h.integrate('msd2', msd2_int_range)

        #Split into Jet 1 score b-tag passing/failing region. 
        print('Processing sample: ', sample)
        
        #Just initialize the values
        hpass=None
        hfail=None

        if sample not in btag_SF_samples:
            
            hpass = sig.integrate('bb1',int_range=slice(bbthr,1.)).sum('genflavor1', overflow='under').integrate('process',sample)
            hfail = sig.integrate('bb1',int_range=slice(0.,bbthr)).sum('genflavor1', overflow='under').integrate('process',sample)
                        
            for s in hfail.identifiers('systematic'):
                    fout[f"Vmass_{i}_pass_{sample}_{s}"] = hist.export1d(hpass.integrate('systematic',s))
                    fout[f"Vmass_{i}_fail_{sample}_{s}"] = hist.export1d(hfail.integrate('systematic',s))
            
        elif sample == 'Wjets': #Divide Wjets into unmatched and matched
            
            hpass_qq = sig.integrate('bb1',int_range=slice(bbthr,1.)).integrate('process',sample).integrate('genflavor1', int_range=slice(1, None))
            hfail_qq = sig.integrate('bb1',int_range=slice(0.,bbthr)).integrate('process',sample).integrate('genflavor1', int_range=slice(1, None))
            
            for s in hpass_qq.identifiers('systematic'):
                
                fout[f"Vmass_{i}_pass_{sample + 'QQ'}_{s}"] = hist.export1d(hpass_qq.integrate('systematic',s))
                fout[f"Vmass_{i}_fail_{sample + 'QQ'}_{s}"] = hist.export1d(hfail_qq.integrate('systematic',s))
                fout[f"Vmass_{i}_fail_{sample + 'QQ'}_{s}"] = hist.export1d(hfail_qq.integrate('systematic',s))
            
                fout[f"Vmass_{i}_fail_{sample + 'QQ'}_{s}"] = hist.export1d(hfail_qq.integrate('systematic',s))       
            
        else: #Divide Zjets into Z(qq) and Z(bb)
            
            hpass = sig.integrate('genflavor1', int_range=slice(1,3)).integrate('bb1',int_range=slice(bbthr,1.)).integrate('process',sample)
            hfail = sig.integrate('genflavor1', int_range=slice(1,3)).integrate('bb1',int_range=slice(0.,bbthr)).integrate('process',sample)
            
            hpass_bb = sig.integrate('genflavor1', int_range=slice(3,4)).integrate('bb1',int_range=slice(bbthr,1.)).integrate('process',sample)
            hfail_bb = sig.integrate('genflavor1', int_range=slice(3,4)).integrate('bb1',int_range=slice(0.,bbthr)).integrate('process',sample)
            
            for s in hfail.identifiers('systematic'):
                fout[f"Vmass_{i}_pass_{sample}_{s}"] = hist.export1d(hpass.integrate('systematic',s))
                fout[f"Vmass_{i}_fail_{sample}_{s}"] = hist.export1d(hfail.integrate('systematic',s))
                    
                fout[f"Vmass_{i}_pass_{sample + 'bb'}_{s}"] = hist.export1d(hpass_bb.integrate('systematic',s))
                fout[f"Vmass_{i}_fail_{sample + 'bb'}_{s}"] = hist.export1d(hfail_bb.integrate('systematic',s))

    return

def process_muonCR(fout, sample, filenames):

    #Read in the pickle file
    template = make_template(filenames)

    h = template.integrate('region','muoncontrol').sum('genflavor1', overflow='all')

    #Split the muon CR into pass and fail region
    hpass = h.integrate('bb1',int_range=slice(bbthr,1.)).integrate('process',sample)
    hfail = h.integrate('bb1',int_range=slice(0.,bbthr)).integrate('process',sample)
            
    #No systematics for now
    for s in hfail.identifiers('systematic'):
        fout[f"muonCR_pass_{sample}_{s}"] = hist.export1d(hpass.integrate('systematic',s))
        fout[f"muonCR_fail_{sample}_{s}"] = hist.export1d(hfail.integrate('systematic',s))

    return

# Main method
def main():
    
    # Check if pickle exists, remove it if it does
    # Make the output directory
    if os.path.exists(outdir): shutil.rmtree(outdir)
    print(f"Directory '{outdir}' has been removed.")
    os.system('mkdir -p  %s' %outdir)

    out_path = '../vhbb_official/{}/regions.root'.format(year)
    if os.path.isfile(out_path): os.remove(out_path) #If file already exists remove it and create a new file
    out_file = uproot3.create(out_path)

    #Process main histograms 
    for sample in samples:
        sample_label = sample if sample != 'VBFDipoleRecoilOn' else 'VBFHToBBDipoleRecoilOn'

        #Get the sample output dir and then the infiles
        year_dir = f'../coffea/vhbb_official/{year}'

        #Group DYJets into Zjets
        if sample == 'Zjets':
            sample_infiles = subprocess.getoutput(f"ls {year_dir}/Zjets/*.coffea").split() + subprocess.getoutput(f"ls {year_dir}/DYJets/*.coffea").split()

        else:
            sample_infiles = subprocess.getoutput(f"ls {year_dir}/{sample_label}/*.coffea").split()


        print("---------------")
        print(f"Processing sample: {sample}")
        print(f"Coffea Files: {sample_infiles}")
        process(out_file, sample, sample_infiles)

    #Process muon CR
    for sample in muonCR_samples:
        coffea_files =  [f'../coffea/muonCR/{year}/{year}_dask_{sample}.coffea']
        print(f"Processing muonCR sample: {sample}. Coffea file: {coffea_files}")
        process_muonCR(out_file, sample, coffea_files)

    #Now process theory systematics

if __name__ == "__main__": main()