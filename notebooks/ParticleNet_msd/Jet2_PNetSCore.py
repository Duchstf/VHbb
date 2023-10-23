import os, subprocess
import json
import uproot3
import awkward as ak
import numpy as np
from coffea import processor, util, hist
import pickle
import pandas as pd

#Plot settings
import matplotlib.pyplot as plt
import mplhep as hep
plt.style.use(hep.style.CMS)


pickle_path = '../../output/pickle/pnet_scan_msd_QCD_Oct17_2023/2017/ParticleNet_msd.pkl'
coffea_hist = pickle.load(open(pickle_path,'rb')) #Load the templates

samples = [ 'QCD',
            'WH','ZH',
            'VV',
            'Wjets', 'Zjets',
            'VBFDipoleRecoilOff', #Double checking this.
            'ggF', 
            'singlet',
            'ttH',
            'ttbarBoosted']

for sample in samples:
    plt.figure()
    hist.plot1d(coffea_hist.integrate('region','signal').sum('genflavor2',
                                                             'msd1',
                                                             'bb1','cc2','qcd2','qq2',overflow='all').integrate('process', sample), density=False)
    plt.legend([sample])
    plt.xlabel('Jet 2 BB Scores')
    plt.show()
    plt.savefig('plots/bb2_{}.pdf'.format(sample))
    plt.savefig('plots/bb2_{}.png'.format(sample))
    
    
for sample in samples:
    plt.figure()
    hist.plot1d(coffea_hist.integrate('region','signal').sum('genflavor2',
                                                             'msd1',
                                                             'bb1','cc2','bb2','qq2',overflow='all').integrate('process', sample), density=False)
    plt.legend([sample])
    plt.xlabel('Jet 2 QCD Scores')
    plt.show()
    plt.savefig('plots/qcd2_{}.pdf'.format(sample))
    plt.savefig('plots/qcd2_{}.png'.format(sample))
    

for sample in samples:
    plt.figure()
    hist.plot1d(coffea_hist.integrate('region','signal').sum('genflavor2',
                                                             'msd1',
                                                             'bb1','cc2','bb2','qcd2',overflow='all').integrate('process', sample), density=False)
    plt.legend([sample])
    plt.xlabel('Jet 2 QQ Scores')
    plt.show()
    plt.savefig('plots/qq2_{}.pdf'.format(sample))
    plt.savefig('plots/qq2_{}.png'.format(sample))


