
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
fig_size = (16,12)

def plot_2D_mass(h, p):

    h_plot = h.sum('genflavor1', 'genflavor2', overflow='all').integrate('process', p)

    p_name = p if p != 'VBFDipoleRecoilOn' else 'VBF'

    #Before bb cutting
    plt.figure(figsize=fig_size)
    hist.plot2d(h_plot.sum('bb1'), xaxis="msd1")
    plt.xlabel(r'Jet 1 $m_{sd}$ [GeV] ')
    plt.ylabel(r'Jet 2 $m_{sd}$ [GeV] ')
    plt.title(p_name)
    plt.savefig(f'plots/mass2D_{p}_all.pdf', bbox_inches='tight')

    #After bb cutting
    plt.figure(figsize=fig_size)
    hist.plot2d(h_plot.integrate('bb1', slice(0.9880, 1.)), xaxis="msd1")
    plt.xlabel(r'Jet 1 $m_{sd}$ [GeV] ')
    plt.ylabel(r'Jet 2 $m_{sd}$ [GeV] ')
    plt.title(f'{p_name} bb pass')
    plt.savefig(f'plots/mass2D_{p}_bbpass.pdf', bbox_inches='tight')

    return

def plot_flavor_stack(h, process='QCD', stack_axis='genflavor1', bb_pass =True):

    labels = ['unmatched','light','charm','bottom']
    fig, ax = plt.subplots(figsize=fig_size)

    total_h = h.sum(stack_axis, overflow='all').to_hist()
    hists = [h.integrate(stack_axis, slice(None,1),overflow='under').to_hist()] + [h.integrate(stack_axis, slice(i,i+1)).to_hist() for i in range(1,4)]

    # Integrate all MC histograms into one
    total_val = total_h.view().value
    total_errors = np.sqrt(total_h.view().variance)  # Calculate standard deviation from variance

    # Plot stacked MC histograms
    colors = ['#94a4a2', '#832db6', '#bd1f01', 'sandybrown']
    cumulative_hist = np.zeros_like(hists[0].view().value)
    previous_cumulative_hist = np.zeros_like(hists[0].view().value)

    for hist_data, color, label in zip(hists, colors, labels):
        cumulative_hist += hist_data.view().value
        ax.fill_between(hist_data.axes[0].centers, previous_cumulative_hist, cumulative_hist, step='mid', alpha=0.5, color=color, label=label)
        previous_cumulative_hist += hist_data.view().value

    # Plot MC statistical uncertainties as hatches
    hist_centers = total_h.axes[0].centers
    ax.fill_between(hist_centers, total_val - total_errors, total_val + total_errors,
                     step='mid', alpha=0.2, color='none', edgecolor='gray', hatch='//', linewidth=0)
    
    if stack_axis == 'genflavor1': 
        x_axis_label=r'Jet 1 $m_{sd}$ [GeV]'
        msd_label = 'msd1'
    else: 
        x_axis_label=r'Jet 2 $m_{sd}$ [GeV]'
        msd_label = 'msd2'

    p_name = process if process != 'VBFDipoleRecoilOn' else 'VBF'
    include_label = 'bbpass' if bb_pass else 'all'
    include_title = f'{p_name} BB Pass' if bb_pass else p_name

    #Plot settings
    plt.legend(labels=labels)
    plt.xlabel(x_axis_label)
    plt.ylabel('Events')
    plt.title(include_title)
    plt.savefig(f'plots/{process}_{msd_label}_{include_label}.pdf', bbox_inches='tight')


def plot_flavor(h, p):

    labels = ['unmatched','light','charm','bottom']

    h_plot_1_all = h.sum('bb1','msd2', 'genflavor2', overflow='all').integrate('process', p)
    h_plot_1_pass = h.sum('msd2', 'genflavor2', overflow='all').integrate('process', p).integrate('bb1', slice(0.9880, 1.))

    h_plot_2_all = h.sum('bb1', 'msd1', 'genflavor1', overflow='all').integrate('process', p)
    h_plot_2_pass = h.sum('msd1', 'genflavor1', overflow='all').integrate('process', p).integrate('bb1', slice(0.9880, 1.))

    plot_flavor_stack(h_plot_1_all, p, stack_axis='genflavor1', bb_pass=False)
    plot_flavor_stack(h_plot_1_pass, p, stack_axis='genflavor1', bb_pass=True)

    plot_flavor_stack(h_plot_2_all, p, stack_axis='genflavor2', bb_pass=False)
    plot_flavor_stack(h_plot_2_pass, p, stack_axis='genflavor2', bb_pass=True)

    
    return

def main():
    
    pickle_path = '/uscms_data/d3/dhoang/VH_analysis/CMSSW_10_2_13/src/VHbb/output/pickle/vhbb_2dmass/2018/h.pkl'
    
    #Same in make_cards.py
    samples = ['QCD','VV','Wjets', 'Zjets',
                'VBFDipoleRecoilOn','ggF','ttH', 'WH','ZH','HH',
                'singlet', 'ttbar']

    h = pickle.load(open(pickle_path,'rb')).integrate('region','signal').integrate('systematic', 'nominal').integrate('qcd2', slice(0.0, 0.0741))
    
    for p in samples:
        print("Processing ", p)
        plot_2D_mass(h, p)
        plot_flavor(h, p)

if __name__ == "__main__":
    main()
