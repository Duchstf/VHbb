import json
import matplotlib.pyplot as plt
from matplotlib.pyplot import cm
import mplhep as hep
import sys
plt.style.use(hep.style.ROOT)

import matplotlib.pylab as pylab
params = {'legend.fontsize': 'medium',
         'axes.labelsize': 'x-large',
         'axes.titlesize':'x-large',
         'xtick.labelsize':'medium',
         'ytick.labelsize':'medium'}
pylab.rcParams.update(params)

from coffea import hist
import pickle

import numpy as np

#Dataset parameters
lumis = {}
lumis['2016'] = 35.9
lumis['2017'] = 41.5
lumis['2018'] = 59.9

def plot_dist(h):
    
    #Plot pt distribution
    h_pt = h.sum('qcd', 'rho')
    ax_pt = hist.plot1d(h_pt)
    handles_pt, labels_pt = ax_pt.get_legend_handles_labels()
    labels_pt[labels_pt.index('None')] = 'QCD' # Modify the labels list as desired
    ax_pt.legend(handles_pt, labels_pt) # Set the new labels
    plt.xlabel(r'Jet 1 $p_T$ [GeV]')
    # plt.xlim([450,1350])
    # plt.ylim([0., 2e+6])
    plt.show()
    plt.savefig("plots/pt_dist.pdf")
    
    #Plot qcd distribution
    plt.figure()
    h_qcd = h.sum('pt', 'rho')
    ax_qcd = hist.plot1d(h_qcd)
    handles, labels = ax_qcd.get_legend_handles_labels()
    labels[labels.index('None')] = 'QCD' # Modify the labels list as desired
    ax_qcd.legend(handles, labels) # Set the new labels
    plt.xlabel(r'ParticleNetMD QCD Scores [GeV]')
    plt.xlim([0,1])
    plt.show()
    plt.savefig("plots/qcd_dist.pdf")
    
    #Plot rho distribution
    plt.figure()
    h_rho = h.sum('pt', 'qcd')
    ax_rho = hist.plot1d(h_rho)
    handles, labels = ax_rho.get_legend_handles_labels()
    labels[labels.index('None')] = 'QCD' # Modify the labels list as desired
    ax_rho.legend(handles, labels) # Set the new labels
    plt.xlabel(r"$\rho=ln(m^2_{reg}/p_T^2)$")
    plt.xlim([-8,-0.5])
    plt.show()
    plt.savefig("plots/rho_dist.pdf")
    
    #Plot 2D distributions of jet pt and qcd scores
    plt.figure()
    h_pt_qcd = h.sum('rho')
    hist.plot2d(h_pt_qcd, xaxis="qcd", patch_opts={'norm': plt.Normalize(vmin=0, vmax=80)})
    plt.ylabel(r'Jet $p_T$ [GeV] ')
    plt.xlabel(r'ParticleNet MD QCD Scores')
    plt.savefig(f'plots/pt_qcd_dist.pdf', bbox_inches='tight')
    
    #Plot 2D distributions of jet pt and qcd scores
    plt.figure()
    h_rho_pt = h.sum('qcd')
    hist.plot2d(h_rho_pt, xaxis="rho", patch_opts={'norm': plt.Normalize(vmin=0, vmax=80)})
    plt.ylabel(r'Jet $p_T$ [GeV] ')
    plt.xlabel(r"$\rho=ln(m^2_{reg}/p_T^2)$")
    plt.savefig(f'plots/pt_rho_dist.pdf', bbox_inches='tight')

def derive_ddt(h):
    pass
    
def main():
    
    year = sys.argv[1]
    pickle_path = f'../../output/pickle/ddt_map/{year}/h.pkl'
    h = pickle.load(open(pickle_path,'rb')).integrate('region','signal').integrate('process', 'QCD')
    
    #Derive the ddtmap
    plot_dist(h)
    #derive_ddt(h)
    
if __name__ == "__main__":
    main()