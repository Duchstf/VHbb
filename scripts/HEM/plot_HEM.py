
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

# Plotting environment vhbb
labels = {
    'QCD': ['QCD'],
    'VV': ['VV'],
    'VH': ['WH', 'ZH'],
    'Bkg Higgs': ['VBFDipoleRecoilOn', 'ggF', 'ttH'],
    'TTbar': ['ttbar'],
    'Single T': ['singlet'],
    'W + jets': ['Wjets'],
    'Z + jets': ['Zjets']
}

colors = {
    'QCD': '#94a4a2',
    'VV': '#e31a1c',
    'VH': '#33a02c',
    'Bkg Higgs': '#1f78b4',
    'TTbar': '#ff7f00',
    'Single T': '#6a3d9a',
    'W + jets': '#b15928',
    'Z + jets': '#cab2d6'
}


def plot_1d(h, x_axis='eta1'):

    mc_labels = labels.keys()
    year = '2018'

    # Create figure and axis
    fig = plt.figure()
    ax1 = fig.add_subplot(4, 1, (1, 3))
    plt.subplots_adjust(hspace=0)

    # Prepare MC histograms
    mc_hists = []
    for label, processes in labels.items():
        if isinstance(processes, list):
            combined_hist = sum(h[{'process': process}] for process in processes)
        else:
            combined_hist = h[{'process': processes}]
        mc_hists.append((combined_hist[5:35], label))

    data_hist = h[{'process': 'data'}][5:35]

    # Integrate all MC histograms into one
    total_mc_hist = sum(hist_data for hist_data, _ in mc_hists)
    total_mc_values = total_mc_hist.view().value
    total_mc_errors = np.sqrt(total_mc_hist.view().variance)  # Calculate standard deviation from variance

       # Plot stacked MC histograms
    cumulative_hist = np.zeros_like(total_mc_values)
    previous_cumulative_hist = np.zeros_like(total_mc_values)
    for hist_data, label in mc_hists:
        cumulative_hist += hist_data.view().value
        ax1.fill_between(hist_data.axes[0].centers, previous_cumulative_hist, cumulative_hist, step='mid', alpha=0.5, color=colors[label], label=label)
        previous_cumulative_hist += hist_data.view().value

    # Plot MC statistical uncertainties as hatches
    mc_centers = total_mc_hist.axes[0].centers
    ax1.fill_between(mc_centers, total_mc_values - total_mc_errors, total_mc_values + total_mc_errors,
                     step='mid', alpha=0.2, color='none', edgecolor='gray', hatch='//', linewidth=0)

    hep.cms.label('Preliminary', lumi=lumis[year], data=True, year=year)
    data_hist.plot(ax=ax1, histtype='errorbar', color='k', marker='o', label='Data')
    ax1.set_xlim([-3.3, 3.3])
    ax1.set_yscale('log')
    legend = ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left')

    # Ratio plot
    data_values = data_hist.view().value
    data_errors = np.sqrt(data_hist.view().variance)

    # Calculate the ratio and its errors
    ratio = data_values / total_mc_values
    ratio_errors =ratio * np.sqrt((data_errors / data_values)**2 + (total_mc_errors / total_mc_values)**2)
    
    ax2 = fig.add_subplot(4, 1, (4, 4))
    ax2.errorbar(mc_centers, ratio, yerr=ratio_errors, fmt='o', color='k', markersize=5)

    ax2.set_ylabel(r'$Data/MC$')

    x_label = r'Fat Jet $\phi$' if x_axis == 'phi1' else r'Fat Jet $\eta$'
    ax2.set_xlabel(x_label)
    ax2.set_xlim(ax1.get_xlim())
    ax2.set_ylim(0, 2)

    # Add horizontal line at 1
    ax2.axhline(1, color='black', linestyle='--', linewidth=1)
    plt.savefig(f'plots/HEM_{x_axis}.pdf', bbox_inches='tight')

def main():
    
    pickle_path = '/uscms_data/d3/dhoang/VH_analysis/CMSSW_10_2_13/src/VHbb/output/pickle/vhbb_HEM/2018/h.pkl'

    h = pickle.load(open(pickle_path,'rb')).integrate('region','signal').integrate('systematic', 'nominal')

    h_phi = h.sum('eta1').to_hist()
    h_eta = h.sum('phi1').to_hist()

    #Plot MC/data
    plot_1d(h_phi, x_axis='phi1')
    plot_1d(h_eta, x_axis='eta1')

if __name__ == "__main__":
    main()
