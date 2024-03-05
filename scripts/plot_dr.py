import json
import matplotlib.pyplot as plt
from matplotlib.pyplot import cm
import mplhep as hep
plt.style.use(hep.style.ROOT)

import matplotlib.pylab as pylab
params = {'legend.fontsize': 'medium',
         'axes.labelsize': 'x-large',
         'axes.titlesize':'x-large',
         'xtick.labelsize':'medium',
         'ytick.labelsize':'medium'}
pylab.rcParams.update(params)

#line thickness
import matplotlib as mpl
mpl.rcParams['lines.linewidth'] = 5

from coffea import hist
import pickle
    
# Main method
def main():
    
    pickle_path = '../output/pickle/vhbb_v3_msd2/2017/ParticleNet_msd.pkl' #Need to be defined manually
    
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
    p = ['singlet']
    h = pickle.load(open(pickle_path,'rb')).integrate('region','signal').integrate('systematic', 'nominal').sum( 'bb1', 'cc2', 'msd1', 'msd2')
    hp = h.integrate('process',p)
    #print(hp.sum('msd1', 'msd2').values())
    ax = hist.plot1d(hp)
    
    # If you want to change the legend label later, find the handle and label of the legend
    handles, labels = ax.get_legend_handles_labels()

    # Modify the labels list as desired
    labels[labels.index('None')] = p[0]

    # Set the new labels
    ax.legend(handles, labels)

    plt.xlabel(r'dR between two leading jets')
    #plt.savefig('plots/dR_VH.pdf', bbox_inches='tight')
    plt.savefig(f'plots/dR_{p[0]}.png', bbox_inches='tight')
    

if __name__ == "__main__":
    main()
