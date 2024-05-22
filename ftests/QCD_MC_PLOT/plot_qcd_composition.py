import os, sys
import subprocess
import json
import numpy as np
from coffea import processor, util, hist
import pickle
import matplotlib.pyplot as plt

year = '2016APV'

bb_WPs = { '2016APV_bb1': 0.9883, '2016_bb1': 0.9883, '2017_bb1': 0.9870, '2018_bb1':  0.9880}
qcd_WPs = { '2016APV_qcd2': 0.0541, '2016_qcd2': 0.0882, '2017_qcd2': 0.0541, '2018_qcd2':  0.0741}

with open('../../files/xsec.json') as f: xs = json.load(f)
with open('../../files/pmap.json') as f: pmap = json.load(f)
with open('../../files/lumi.json') as f: lumis = json.load(f)

filename = f"../../output/coffea/vhbb_official/{year}/{year}_dask_QCD.coffea"
outsum = processor.dict_accumulator()

#Define the score threshold
bbthr = bb_WPs[f'{year}_bb1']
print(f'BB1 {year} Threshold: ', bbthr)

qcdthr = qcd_WPs[f'{year}_qcd2']
print(f'QCD 2 {year} Threshold: ', qcdthr)

hist_name = 'h'
started = 0
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
templates = outsum[hist_name].integrate('systematic','nominal').integrate('region','signal').integrate('qcd2', slice(0., qcdthr)).integrate('pt1', slice(450, None), overflow='over').sum('genflavor1', overflow='under')

passhists = []
failhists = []

qcd_samples = ["QCD_HT100to200", "QCD_HT200to300", "QCD_HT300to500", "QCD_HT500to700", "QCD_HT700to1000", "QCD_HT1000to1500", "QCD_HT1500to2000", "QCD_HT2000toInf"]
mass_range = [40., 68., 110., 201.]

for i in range(len(mass_range)-1):
    msd2_int_range = slice(mass_range[i], mass_range[i+1])
    sig = templates.integrate('msd2', msd2_int_range)

    passhists += [sig.integrate('bb1',int_range=slice(bbthr,1.))]
    failhists += [sig.integrate('bb1',int_range=slice(0.,bbthr))]

#Plot them out
for i in range(len(mass_range)-1):
    colors = ['#94a4a2','#832db6','#bd1f01','sandybrown','gold','lime','green','deepskyblue']

    fig = plt.figure()
    hist.plot1d(passhists[i], overlay='dataset', order=qcd_samples, stack=True, fill_opts={'edgecolor':'black', 'color':colors})
    plt.savefig(f'plots/{year}_Vbin{i}_pass.pdf')

    fig = plt.figure()
    hist.plot1d(failhists[i], overlay='dataset', order=qcd_samples, stack=True, fill_opts={'edgecolor':'black', 'color':colors})
    plt.savefig(f'plots/{year}_Vbin{i}_fail.pdf')
    