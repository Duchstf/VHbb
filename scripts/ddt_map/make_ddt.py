'''
Make DDT MAP Script.

Usage:
python make_ddt.py <year>
'''
import json
import matplotlib.pyplot as plt
from matplotlib.pyplot import cm
import mplhep as hep
import sys
plt.style.use(hep.style.ROOT)
import scipy.ndimage as sc
import math
import pickle

import os, sys
import subprocess
import json
from coffea import processor, util, hist
import pickle

year = sys.argv[1]

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
    plt.xlabel(r"$\rho=ln(m^2_{SD}/p_T^2)$")
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
    plt.xlabel(r"$\rho=ln(m^2_{SD}/p_T^2)$")
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
    ddtmap = index_to_cut_value(index_qcd_cut) #This is the ddt map
    smooth_ddtmap=sc.filters.gaussian_filter(ddtmap,3,mode='nearest')
    print("Max QCD Cut: ", np.max(ddtmap))
    print("Min QCD Cut: ", np.min(ddtmap))
    
    #Display the ddt map
    plt.figure()
    
    # Calculate extent: [xmin, xmax, ymin, ymax]
    # We use x_values[0], x_values[-1], y_values[0], and y_values[-1]
    # We adjust the max values by adding the step size to align with the pixel edges
    x_step = rho_edges[1] - rho_edges[0]
    y_step = pt_edges[1] - pt_edges[0]
    extent = [rho_edges[0], rho_edges[-1] + x_step, pt_edges[0], pt_edges[-1] + y_step]
    im = plt.imshow(smooth_ddtmap, cmap='viridis', aspect='auto', extent=extent, vmin=0., vmax=0.2)  # Display the data as an image, 'viridis' is a color map

    # Add a colorbar to show the color scale
    plt.colorbar(im, label=f'QCD Cuts at {round(eff*100)} %')
    
    # Add labels and title if desired
    plt.xlabel(r"$\rho=ln(m^2_{SD}/p_T^2)$")
    plt.ylabel(r'$p_T$ [GeV]')
    hep.cms.text(f"V(qq)H(bb) DDT Map, {year}")

    # Show the plot
    plt.savefig(f'plots/{year}_ddt_map.pdf', bbox_inches='tight')
    
    return smooth_ddtmap, pt_edges, rho_edges
    
def find_QCD_eff(h, qcd_cut):
    print("Finding qcd efficiency")
    print(h.sum('pt', 'qcd', 'rho'))
    total = h.sum('pt', 'qcd', 'rho').values()[()]
    remaining = h.integrate('qcd', slice(0.,qcd_cut)).sum('pt', 'rho').values()[()]
    eff = remaining/total
    print(f"QCD Efficiency for {qcd_cut}: ", round(eff,4))
    return eff

def make_hist(out_dir):

    #Load all the files
    with open('../../files/xsec.json') as f: xs = json.load(f)     
    with open('../../files/pmap.json') as f: pmap = json.load(f)
    with open('../../files/lumi.json') as f: lumis = json.load(f)

    hist_name = 'h' #You need to define this manually, usually just keep it as "templates"
            
    infiles = subprocess.getoutput(f"ls {out_dir}/*.coffea").split()
    outsum = processor.dict_accumulator()

    started = 0
    for filename in infiles:

        print("Loading "+filename)
        
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

    return templates
    
def main():

    out_dir = f'../../output/coffea/DDT/{year}/QCD'
    
    h = make_hist(out_dir).integrate('region', 'signal').integrate('process' ,'QCD')
    
    #Derive the ddtmap
    #plot_dist(h, year)
    eff = find_QCD_eff(h, qcd_cut=0.0741)
    smooth_ddtmap, pt_edges, rho_edges = derive_ddt(h, year, eff=eff)
    
    data_dir = f'../../boostedhiggs/data'
    np.save(f'{data_dir}/ddtmap_{year}.npy', smooth_ddtmap)
    np.save(f'{data_dir}/ddtmap_ptedges.npy', pt_edges)
    np.save(f'{data_dir}/ddtmap_rhoedges.npy', rho_edges)
    
if __name__ == "__main__":
    main()