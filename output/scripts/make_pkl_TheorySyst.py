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
import numpy as np
import uproot3
import shutil

#Load all the files
with open('../../files/xsec.json') as f: xs = json.load(f)     
with open('../../files/pmap.json') as f: pmap = json.load(f)
with open('../../files/lumi.json') as f: lumis = json.load(f)
bb_WPs = { '2016APV_bb1': 0.9883, '2016_bb1': 0.9883, '2017_bb1': 0.9870, '2018_bb1':  0.9880}
qcd_WPs = { '2016APV_qcd2': 0.0741, '2016_qcd2': 0.0741, '2017_qcd2': 0.0741, '2018_qcd2':  0.0741}
theory_syst_samples = ['VV', 'VBFDipoleRecoilOn','ggF','ttH', 'WH','ZH']
scalevar_map = {'VV':3, 'ggF':7, 'ttH':7, 'WH':3, 'ZH':3, 'VBFDipoleRecoilOn':3}
if len(sys.argv) < 2: raise Exception("Enter year.") # Take in the year and tag

year = sys.argv[1]
tag = "vhbb_theory_systematics"
outdir = '../{}/{}'.format(tag,year)

#Define the score threshold
bbthr = bb_WPs[f'{year}_bb1']
print(f'BB1 {year} Threshold: ', bbthr)

qcdthr = qcd_WPs[f'{year}_qcd2']
print(f'QCD 2 {year} Threshold: ', qcdthr)

# run this per msd2 bin
def reduce_scalevar(h, point=7):

    # Recommendation from LHC H WG is 3 point for VH, VBF and 7 point for ggF, ttH

    # Read in all the up histograms, conver to numpy arrays
    values = [h.integrate('systematic','scalevar_'+str(i)+'Up')._sumw[()] for i in range(0,9)]
    errors = [h.integrate('systematic','scalevar_'+str(i)+'Up')._sumw2[()] for i in range(0,9)]

    hists = np.array(values)
    hists_errors = np.array(errors)

    if point == 7:
        up = hists[0]
        down = hists[0]
        up_errors = hists_errors[0]
        down_errors = hists_errors[0]
        
        for i in range(1, 9):
            mask_up = hists[i] > up
            mask_down = hists[i] < down
            up = np.where(mask_up, hists[i], up)
            down = np.where(mask_down, hists[i], down)
            up_errors = np.where(mask_up, hists_errors[i], up_errors)
            down_errors = np.where(mask_down, hists_errors[i], down_errors)

    elif point == 3:
        up = np.maximum(hists[0], hists[8])
        down = np.minimum(hists[0], hists[8])
        mask_up = hists[8] > hists[0]
        mask_down = hists[8] < hists[0]
        up_errors = np.where(mask_up, hists_errors[8], hists_errors[0])
        down_errors = np.where(mask_down, hists_errors[8], hists_errors[0])
        
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
def reduce_pdfvar(h):

    # NNPDF31_nnlo_hessian_pdfas
    # https://lhapdfsets.web.cern.ch/current/NNPDF31_nnlo_hessian_pdfas/NNPDF31_nnlo_hessian_pdfas.info

    # Nominal (sigma^0)
    sigma0 = np.array(h.integrate('systematic','PDF_weight_0Up')._sumw[()])
    
    # Hessian PDF weights
    # Eq. 21 of https://arxiv.org/pdf/1510.03865v1.pdf  
    hists_pdf = np.array([h.integrate('systematic','PDF_weight_'+str(i)+'Up')._sumw[()] - sigma0 for i in range(1,101)])
    summed = np.sum(np.square(hists_pdf),axis=0)
    pdf_unc = np.sqrt( (1./99.) * summed ) 

    # alpha_S weights
    # Eq. 27 of same ref
    hists_aS = np.array([h.integrate('systematic','PDF_weight_'+str(i)+'Up')._sumw[()] for i in range(101,103)])
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

def theory_process(sample, coffea_files):

    outpath = os.path.join(outdir, f'{sample}.root')

    #If file already exists remove it and create a new file
    if os.path.isfile(outpath): os.remove(outpath)
    fout = uproot3.create(outpath)
    
    hist_name = 'h' #You need to define this manually, usually just keep it as "templates"
    outsum = processor.dict_accumulator()

    started = 0
    for filename in coffea_files:

        print("Loading "+filename)

        if 'NLO' in filename: continue
        
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

    #Reduce the systematics
    to_reduce_list = ['PDF_weight', 'scalevar']
    templates = templates.integrate('region','signal').integrate('qcd2', slice(0., qcdthr)).integrate('pt1', slice(450, None), overflow='over')
    mass_range = [40., 68., 110., 201.]
    for i in range(len(mass_range)-1):
        print('Running for {} in {} mass region'.format(year, i))
        msd2_int_range = slice(mass_range[i], mass_range[i+1])
        sig = templates.integrate('msd2', msd2_int_range)

        hpass = sig.integrate('bb1',int_range=slice(bbthr,1.)).sum('genflavor1', overflow='under').integrate('process',sample)
        hfail = sig.integrate('bb1',int_range=slice(0.,bbthr)).sum('genflavor1', overflow='under').integrate('process',sample)

        for s in hfail.identifiers('systematic'):
            #Export systematics normally if not reduce
            if not any(term in str(s) for term in to_reduce_list): 
                fout[f"Vmass_{i}_pass_{sample}_{s}"] = hist.export1d(hpass.integrate('systematic',s))
                fout[f"Vmass_{i}_fail_{sample}_{s}"] = hist.export1d(hfail.integrate('systematic',s))
                
        #Reduce the other systematics
        if sample != 'VV': #Skip these for VV for now
            scalevar_syst = f'scalevar_{scalevar_map[sample]}pt'
            scalevar_pass_up, scalevar_pass_down = reduce_scalevar(hpass, point=scalevar_map[sample])
            scalevar_fail_up, scalevar_fail_down = reduce_scalevar(hfail, point=scalevar_map[sample])

            fout[f"Vmass_{i}_pass_{sample}_{scalevar_syst}Up"] = hist.export1d(scalevar_pass_up)
            fout[f"Vmass_{i}_pass_{sample}_{scalevar_syst}Down"] = hist.export1d(scalevar_pass_down)

            fout[f"Vmass_{i}_fail_{sample}_{scalevar_syst}Up"] = hist.export1d(scalevar_fail_up)
            fout[f"Vmass_{i}_fail_{sample}_{scalevar_syst}Down"] = hist.export1d(scalevar_fail_down)

            #Reduce pdf weights
            pdf_weights_syst = 'PDF_weight'
            pdf_weights_pass_up, pdf_weights_pass_down = reduce_pdfvar(hpass)
            pdf_weights_fail_up, pdf_weights_fail_down = reduce_pdfvar(hfail)

            fout[f"Vmass_{i}_pass_{sample}_{pdf_weights_syst}Up"] = hist.export1d(pdf_weights_pass_up)
            fout[f"Vmass_{i}_pass_{sample}_{pdf_weights_syst}Down"] = hist.export1d(pdf_weights_pass_down)

            fout[f"Vmass_{i}_fail_{sample}_{pdf_weights_syst}Up"] = hist.export1d(pdf_weights_fail_up)
            fout[f"Vmass_{i}_fail_{sample}_{pdf_weights_syst}Down"] = hist.export1d(pdf_weights_fail_down)


# Main method
def main():
            
    indir = "../coffea/{}/{}/".format(tag, year)
    infiles = subprocess.getoutput("ls "+indir+year+"_dask_*.coffea").split()
    
    # Check if pickle exists, remove it if it does
    # Make the output directory
    if os.path.exists(outdir): shutil.rmtree(outdir)
    print(f"Directory '{outdir}' has been removed.")
    os.system('mkdir -p  %s' %outdir)

    for sample in theory_syst_samples: 
        coffea_files =  [infile for infile in infiles if sample in infile]
        theory_process(sample, coffea_files)

if __name__ == "__main__":

    main()
