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
scalevar_map = {'VVNLO':3, 'ggF':7, 'ttH':7, 'WH':3, 'ZH':3, 'VBFDipoleRecoilOn':3}

#Define the score threshold
bbthr = bb_WPs[f'{year}_bb1']
qcdthr = 0.0741
mass_range = [40., 68., 110., 201.]

#List the samples
samples = ['QCD', 'VV', 'Wjets', 'Zjets',
           'VBFDipoleRecoilOn','ggF','ttH', 'WH','ZH',
           'singlet', 'ttbar',
           'data']

# samples = ['QCD', 'data']
split_samples = ['Wjets', 'Zjets', 'VV'] #Samples that needed splitting
muonCR_samples = ['QCD', 'singlet', 'ttbar', 'WLNu', "muondata"]

# run this per msd2 bin
def reduce_scalevar(h, sample, point=7):

    # Recommendation from LHC H WG is 3 point for VH, VBF and 7 point for ggF, ttH

    scalevar_length = 9 if sample != 'VVNLO'  else 8

    # Read in all the up histograms, conver to numpy arrays
    values = [h.integrate('systematic','scalevar_'+str(i)+'Up')._sumw[()] for i in range(0,scalevar_length)]
    errors = [h.integrate('systematic','scalevar_'+str(i)+'Up')._sumw2[()] for i in range(0,scalevar_length)]

    hists = np.array(values)
    hists_errors = np.array(errors)

    if point == 7:
        up = hists[0]
        down = hists[0]
        up_errors = hists_errors[0]
        down_errors = hists_errors[0]
        
        for i in range(1, scalevar_length):
            mask_up = hists[i] > up
            mask_down = hists[i] < down
            up = np.where(mask_up, hists[i], up)
            down = np.where(mask_down, hists[i], down)
            up_errors = np.where(mask_up, hists_errors[i], up_errors)
            down_errors = np.where(mask_down, hists_errors[i], down_errors)

    elif point == 3:
        last_index = scalevar_length - 1
        up = np.maximum(hists[0], hists[last_index])
        down = np.minimum(hists[0], hists[last_index])
        mask_up = hists[last_index] > hists[0]
        mask_down = hists[last_index] < hists[0]
        up_errors = np.where(mask_up, hists_errors[last_index], hists_errors[0])
        down_errors = np.where(mask_down, hists_errors[last_index], hists_errors[0])
        
    else:
        print("unknown point value")
    
    scalevar_hist_up = hist.Hist('Events', hist.Bin('msd1', r'Jet 1 $m_{sd}$', 23, 40, 201))
    scalevar_hist_down = hist.Hist('Events', hist.Bin('msd1', r'Jet 1 $m_{sd}$', 23, 40, 201))

    # Set the bin values and errors
    values_up = {(): up}
    errors_up = {(): up_errors}
    values_down = {(): down}
    errors_down = {(): down_errors}

    # Assign values and errors
    scalevar_hist_up._sumw = values_up
    scalevar_hist_up._sumw2 = errors_up
    scalevar_hist_down._sumw = values_down
    scalevar_hist_down._sumw2 = errors_down

    return scalevar_hist_up, scalevar_hist_down

# run this per msd2 bin
def reduce_pdfvar(h, sample):

    # NNPDF31_nnlo_hessian_pdfas
    # https://lhapdfsets.web.cern.ch/current/NNPDF31_nnlo_hessian_pdfas/NNPDF31_nnlo_hessian_pdfas.info

    # Nominal (sigma^0)
    sigma0 = np.array(h.integrate('systematic','PDF_weight_0Up')._sumw[()])

    hessian_length = 101 if sample != 'VVNLO' else 100
    
    # Hessian PDF weights
    # Eq. 21 of https://arxiv.org/pdf/1510.03865v1.pdf  
    hists_pdf = np.array([h.integrate('systematic','PDF_weight_'+str(i)+'Up')._sumw[()] - sigma0 for i in range(1,hessian_length)])
    summed = np.sum(np.square(hists_pdf),axis=0)
    pdf_unc = np.sqrt( (1./99.) * summed ) 

    # alpha_S weights
    # Eq. 27 of same ref
    hists_aS = np.array([h.integrate('systematic','PDF_weight_'+str(i)+'Up')._sumw[()] for i in range(hessian_length, hessian_length+2)])
    as_unc = 0.5*(hists_aS[1] - hists_aS[0]) 

    # PDF + alpha_S weights
    # Eq. 28 of same ref
    pdfas_unc = np.sqrt( np.square(pdf_unc) + np.square(as_unc) ) 

    pdf_hist_up = hist.Hist('Events', hist.Bin('msd1', r'Jet 1 $m_{sd}$', 23, 40, 201))
    pdf_hist_down = hist.Hist('Events', hist.Bin('msd1', r'Jet 1 $m_{sd}$', 23, 40, 201))

    # Set the bin values and errors
    values_up = {(): sigma0 + pdfas_unc}
    errors_up = {(): np.asarray([0.00001] * sigma0.shape[0])}
    values_down = {(): sigma0 - pdfas_unc}
    errors_down = {(): np.asarray([0.00001] * sigma0.shape[0])}

    pdf_hist_up._sumw = values_up
    pdf_hist_up._sumw2 = errors_up
    pdf_hist_down._sumw = values_down
    pdf_hist_down._sumw2 = errors_down

    return pdf_hist_up, pdf_hist_down

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

    h = template.integrate('region','signal').integrate('qcd2', slice(0., qcdthr))

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

        if sample not in split_samples:
            
            hpass = sig.integrate('bb1',int_range=slice(0.9734, 0.9880)).sum('genflavor1', overflow='under').integrate('process',sample)
            hfail = sig.integrate('bb1',int_range=slice(0.,bbthr)).sum('genflavor1', overflow='under').integrate('process',sample)
                        
            for s in hfail.identifiers('systematic'):
                    fout[f"Vmass_{i}_pass_{sample}_{s}"] = hist.export1d(hpass.integrate('systematic',s))
                    fout[f"Vmass_{i}_fail_{sample}_{s}"] = hist.export1d(hfail.integrate('systematic',s))
            
        elif sample == 'Wjets': #Divide Wjets into unmatched and matched
            
            hpass_qq = sig.integrate('bb1',int_range=slice(0.9734, 0.9880)).integrate('process',sample).integrate('genflavor1', int_range=slice(1, None))
            hfail_qq = sig.integrate('bb1',int_range=slice(0.,bbthr)).integrate('process',sample).integrate('genflavor1', int_range=slice(1, None))
            
            for s in hpass_qq.identifiers('systematic'):
                
                fout[f"Vmass_{i}_pass_{sample + 'QQ'}_{s}"] = hist.export1d(hpass_qq.integrate('systematic',s))
                fout[f"Vmass_{i}_fail_{sample + 'QQ'}_{s}"] = hist.export1d(hfail_qq.integrate('systematic',s))
                fout[f"Vmass_{i}_fail_{sample + 'QQ'}_{s}"] = hist.export1d(hfail_qq.integrate('systematic',s))
            
                fout[f"Vmass_{i}_fail_{sample + 'QQ'}_{s}"] = hist.export1d(hfail_qq.integrate('systematic',s))       
            
        elif sample == 'Zjets': #Divide Zjets into Z(qq) and Z(bb)
            
            hpass = sig.integrate('genflavor1', int_range=slice(1,3)).integrate('bb1',int_range=slice(0.9734, 0.9880)).integrate('process',sample)
            hfail = sig.integrate('genflavor1', int_range=slice(1,3)).integrate('bb1',int_range=slice(0.,bbthr)).integrate('process',sample)
            
            hpass_bb = sig.integrate('genflavor1', int_range=slice(3,4)).integrate('bb1',int_range=slice(0.9734, 0.9880)).integrate('process',sample)
            hfail_bb = sig.integrate('genflavor1', int_range=slice(3,4)).integrate('bb1',int_range=slice(0.,bbthr)).integrate('process',sample)
            
            for s in hfail.identifiers('systematic'):
                fout[f"Vmass_{i}_pass_{sample}_{s}"] = hist.export1d(hpass.integrate('systematic',s))
                fout[f"Vmass_{i}_fail_{sample}_{s}"] = hist.export1d(hfail.integrate('systematic',s))
                    
                fout[f"Vmass_{i}_pass_{sample + 'bb'}_{s}"] = hist.export1d(hpass_bb.integrate('systematic',s))
                fout[f"Vmass_{i}_fail_{sample + 'bb'}_{s}"] = hist.export1d(hfail_bb.integrate('systematic',s))
        
        elif sample == 'VV': #Divide VV into VbbVqq and VqqVqq

            hpass = sig.integrate('genflavor1', int_range=slice(1,3)).integrate('bb1',int_range=slice(0.9734, 0.9880)).integrate('process',sample)
            hfail = sig.integrate('genflavor1', int_range=slice(1,3)).integrate('bb1',int_range=slice(0.,bbthr)).integrate('process',sample)
            
            hpass_bb = sig.integrate('genflavor1', int_range=slice(3,4)).integrate('bb1',int_range=slice(0.9734, 0.9880)).integrate('process',sample)
            hfail_bb = sig.integrate('genflavor1', int_range=slice(3,4)).integrate('bb1',int_range=slice(0.,bbthr)).integrate('process',sample)

            for s in hfail.identifiers('systematic'):
                fout[f"Vmass_{i}_pass_VqqVqq_{s}"] = hist.export1d(hpass.integrate('systematic',s))
                fout[f"Vmass_{i}_fail_VqqVqq_{s}"] = hist.export1d(hfail.integrate('systematic',s))
                    
                fout[f"Vmass_{i}_pass_VbbVqq_{s}"] = hist.export1d(hpass_bb.integrate('systematic',s))
                fout[f"Vmass_{i}_fail_VbbVqq_{s}"] = hist.export1d(hfail_bb.integrate('systematic',s))

    return

# Main method
def main():
    
    # Check if pickle exists, remove it if it does
    # Make the output directory
    if os.path.exists(outdir): shutil.rmtree(outdir)
    print(f"Directory '{outdir}' has been removed.")
    os.system('mkdir -p  %s' %outdir)

    out_path = '../mediumWP/{}/regions.root'.format(year)
    if os.path.isfile(out_path): os.remove(out_path) #If file already exists remove it and create a new file
    out_file = uproot3.create(out_path)
    
    #Process main histograms 
    for sample in samples:
        sample_label = sample if sample != 'VBFDipoleRecoilOn' else 'VBFHToBBDipoleRecoilOn'

        #Get the sample output dir and then the infiles
        year_dir = f'../coffea/medium_WP/{year}'
        sample_infiles = subprocess.getoutput(f"ls {year_dir}/{sample_label}/*.coffea").split()

        print("---------------")
        print(f"Processing sample: {sample}")
        print(f"Coffea Files: {sample_infiles}")
        process(out_file, sample, sample_infiles)

if __name__ == "__main__": main()