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

def plot_dist(h, year):
    
    #Plot pt distribution
    h_pt = h.sum('qcd', 'rho')
    ax_pt = hist.plot1d(h_pt)
    handles_pt, labels_pt = ax_pt.get_legend_handles_labels()
    labels_pt[labels_pt.index('None')] = 'QCD' # Modify the labels list as desired
    ax_pt.legend(handles_pt, labels_pt) # Set the new labels
    plt.xlabel(r'Jet 1 $p_T$ [GeV]')
    plt.savefig(f"plots/{year}_pt_dist.pdf")
    
    #Plot qcd distribution
    plt.figure()
    h_qcd = h.sum('pt', 'rho')
    ax_qcd = hist.plot1d(h_qcd)
    handles, labels = ax_qcd.get_legend_handles_labels()
    labels[labels.index('None')] = 'QCD' # Modify the labels list as desired
    ax_qcd.legend(handles, labels) # Set the new labels
    plt.xlabel(r'ParticleNetMD QCD Scores [GeV]')
    plt.xlim([0,1])
    plt.savefig(f"plots/{year}_qcd_dist.pdf")
    
    #Plot rho distribution
    plt.figure()
    h_rho = h.sum('pt', 'qcd')
    ax_rho = hist.plot1d(h_rho)
    handles, labels = ax_rho.get_legend_handles_labels()
    labels[labels.index('None')] = 'QCD' # Modify the labels list as desired
    ax_rho.legend(handles, labels) # Set the new labels
    plt.xlabel(r"$\rho=ln(m^2_{reg}/p_T^2)$")
    plt.xlim([-7,-0.5])
    plt.savefig(f"plots/{year}_rho_dist.pdf")
    
    #Plot 2D distributions of jet pt and qcd scores
    plt.figure()
    h_pt_qcd = h.sum('rho')
    hist.plot2d(h_pt_qcd, xaxis="qcd")
    plt.ylabel(r'Jet $p_T$ [GeV] ')
    plt.xlabel(r'ParticleNet MD QCD Scores')
    plt.savefig(f'plots/{year}_pt_qcd_dist.pdf', bbox_inches='tight')
    
    #Plot 2D distributions of jet pt and qcd scores
    plt.figure()
    h_rho_pt = h.sum('qcd')
    hist.plot2d(h_rho_pt, xaxis="rho")
    plt.ylabel(r'Jet $p_T$ [GeV] ')
    plt.xlabel(r"$\rho=ln(m^2_{reg}/p_T^2)$")
    plt.savefig(f'plots/{year}_pt_rho_dist.pdf', bbox_inches='tight')

def derive_ddt(h, year, eff=0.10):
    print("Total QCD Yield (ignoring overflow): ", h.sum('pt', 'qcd', 'rho').values()[()])
    qcd_cuts = h.axis('qcd').edges()
    pt_edges = h.axis('pt').edges()
    rho_edges = h.axis('rho').edges()
    
    h_values = h.values()[()] #3D array of (rho, pt, and qcd)
    cdf0 = np.cumsum(h_values, axis=2) #cdf along the qcd cut values
    qcd_yield = np.sum(h_values, axis=2)[:, :, np.newaxis] #qcd yield in each rho, pt bin
    cdf = cdf0/qcd_yield #normalize the cdf by the total number of qcd events within that rho, pt bins
    
    #Determine the index of the cut that gives QCD eff
    index_qcd_cut =  np.apply_along_axis(lambda x: x.searchsorted(eff), axis = 2, arr = cdf)
    index_to_cut_value = lambda x: qcd_cuts[x]
    qcd_cuts = index_to_cut_value(index_qcd_cut) #This is the ddt map
    print("Max QCD Cut: ", np.max(qcd_cuts))
    print("Min QCD Cut: ", np.min(qcd_cuts))
    
    #Display the ddt map
    plt.figure()
    
    # Calculate extent: [xmin, xmax, ymin, ymax]
    # We use x_values[0], x_values[-1], y_values[0], and y_values[-1]
    # We adjust the max values by adding the step size to align with the pixel edges
    x_step = rho_edges[1] - rho_edges[0]
    y_step = pt_edges[1] - pt_edges[0]
    extent = [rho_edges[0], rho_edges[-1] + x_step, pt_edges[0], pt_edges[-1] + y_step]
    im = plt.imshow(qcd_cuts, cmap='viridis', aspect='auto', extent=extent, vmin=0., vmax=1.)  # Display the data as an image, 'viridis' is a color map

    # Add a colorbar to show the color scale
    plt.colorbar(im, label=f'QCD Cuts at {int(eff*100)} %')
    
    # Add labels and title if desired
    plt.xlabel(r"$\rho=ln(m^2_{reg}/p_T^2)$")
    plt.ylabel(r'$p_T$ [GeV]')
    hep.cms.text(f"V(qq)H(bb) DDT Map, {year}")

    # Show the plot
    plt.savefig(f'plots/{year}_ddt_map.pdf', bbox_inches='tight')
    
def main():
    
    year = sys.argv[1]
    pickle_path = f'../../output/pickle/ddt_map/{year}/h.pkl'
    h = pickle.load(open(pickle_path,'rb')).integrate('region','signal').integrate('process', 'QCD')
    
    #Derive the ddtmap
    # plot_dist(h, year)
    derive_ddt(h,year,eff=0.26)
    
if __name__ == "__main__":
    main()