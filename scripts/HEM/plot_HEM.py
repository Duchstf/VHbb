
import json
import sys
import matplotlib.pyplot as plt
from matplotlib.pyplot import cm
import mplhep as hep
plt.style.use(hep.style.ROOT)

from coffea import hist
import pickle
import numpy as np

import matplotlib.pylab as pylab
params = {'legend.fontsize': 'medium',
         'axes.labelsize': 'x-large',
         'axes.titlesize':'x-large',
         'xtick.labelsize':'medium',
         'ytick.labelsize':'medium'}
pylab.rcParams.update(params)


#Dataset parameters
lumis = {}
lumis['2016'] = 16.81
lumis['2016APV'] = 19.52
lumis['2017'] = 41.5
lumis['2018'] = 59.9

#Ploting environment vhbb
labels = {
    # 'TTbar': 'ttbar',
    # 'Single T': 'singlet',
    # 'W(Lep.)':'Wjets',
    # 'Z + jets':'Zjets', #'#2ca02c'
    'QCD':'QCD',  
}

colors = ['#94a4a2']


def plot_1d(h, x_axis='phi1'):

    mc = list(labels.values())
    year='2018'

    # Create figure and axis
    fig = plt.figure()
    ax1 = fig.add_subplot(4, 1, (1, 3))
    plt.subplots_adjust(hspace=0)

    # Prepare MC histograms
    mc_hists = [h[{'process': process}] for process in mc]

    # Integrate all MC histograms into one
    total_mc_hist = sum(mc_hists)
    total_mc_values = total_mc_hist.view().value
    total_mc_errors = np.sqrt(total_mc_hist.view().variance)  # Calculate standard deviation from variance

    # Plot stacked MC histograms
    cumulative_hist = np.zeros_like(mc_hists[0].view().value)
    previous_cumulative_hist = np.zeros_like(mc_hists[0].view().value)
    for hist_data, color, label in zip(mc_hists, colors, mc):
        cumulative_hist += hist_data.view().value
        ax1.fill_between(hist_data.axes[0].centers, previous_cumulative_hist, cumulative_hist, step='mid', alpha=0.5, color=color, label=label)
        previous_cumulative_hist += hist_data.view().value

    # Plot MC statistical uncertainties as hatches
    mc_centers = total_mc_hist.axes[0].centers
    ax1.fill_between(mc_centers, total_mc_values - total_mc_errors, total_mc_values + total_mc_errors,
                     step='mid', alpha=0.2, color='none', edgecolor='gray', hatch='//', linewidth=0)
    

    hep.cms.label('Preliminary', lumi=lumis[year], data=True, year=year)
    ax1.set_xlim([-3.5,3.5])
    ax1.set_yscale('log')
    legend = ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left') 

    # Ratio plot
    ax2 = fig.add_subplot(4, 1, (4, 4))
    # data_values = data_hist.view().value
    # data_errors = np.sqrt(data_hist.view().variance)
    
    # Calculate the ratio and its errors
    # ratio = data_values / total_mc_values
    # ratio_errors =ratio * np.sqrt((data_errors / data_values)**2 + (total_mc_errors / total_mc_values)**2)
    
    # ax2.errorbar(mc_centers, ratio, yerr=ratio_errors, fmt='o', color='k', markersize=5)
    ax2.set_ylabel(r'$Data/MC$')
    ax2.set_xlabel(r'Fat Jet $\phi$')
    ax2.set_xlim(ax1.get_xlim())
    ax2.set_ylim(0, 2)
    
    # Add horizontal line at 1
    ax2.axhline(1, color='black', linestyle='--', linewidth=1)
    
    plt.savefig(f'plots/HEM_{x_axis}.pdf', bbox_inches='tight')



def main():
    
    pickle_path = '/uscms_data/d3/dhoang/VH_analysis/CMSSW_10_2_13/src/VHbb/output/pickle/vhbb_HEM/2018/h.pkl'
    
    #Same in make_cards.py
    # samples = ['QCD','VV','Wjets', 'Zjets',
    #             'VBFDipoleRecoilOn','ggF','ttH', 'WH','ZH','HH',
    #             'singlet', 'ttbar']
    

    h = pickle.load(open(pickle_path,'rb')).integrate('region','signal').integrate('systematic', 'nominal')

    h_phi = h.sum('eta1').to_hist()
    h_eta = h.sum('phi1').to_hist()

    #Plot MC/data
    plot_1d(h_phi, x_axis='phi1')

if __name__ == "__main__":
    main()
