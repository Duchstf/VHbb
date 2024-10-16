import os,sys
import argparse
import numpy as np
import ROOT as r
import matplotlib
matplotlib.use("Agg")
import uproot
import matplotlib.pyplot as plt
import hist
import mplhep as hep
plt.style.use(hep.style.ROOT)
import matplotlib.transforms as transforms


def skim_gofs(file_names):
    out = {}
    for i, fname in enumerate(file_names):
        try:
            rfile = r.TFile.Open(fname)
            rtree = rfile.Get("limit")
            for j in range(rtree.GetEntries()):
                rtree.GetEntry(j)
                mu = rtree.limit
                _fname = fname.split("/")[-1].replace("BaseToys", "Toys").replace("AltToys", "Toys")
                out[_fname+":"+str(j)] = mu
        except:
            print("        Skipping: {}".format(fname.split("/")[-1]))
            pass
    return out

def fgofs(gofs_base, gofs_alt, data_ref, data_alt, ref, alt, year="2016", mc=False, savename=None):
    ref_pt, ref_rho = ref
    alt_pt, alt_rho = alt
    
    fig, ax = plt.subplots()
    ax.hist(gofs_base, alpha=0.5, label="Base - toys", bins=30, color='r')
    ax.hist(gofs_alt, alpha=0.5, label="Alt - toys", bins=30, color='blue');
    ax.axvline(data_ref, label="Base - ref", color='red')
    ax.axvline(data_alt, label="Alt - ref", color='blue')
    ax.legend()

    title = "TF({},{}) x TF({},{})".format(ref_pt, ref_rho, alt_pt, alt_rho)
    ax.legend(title=title, loc="best")
    hep.cms.label(data=not mc, year=year, ax=ax)
    x_lim = max(np.percentile(gofs_base, 90), np.percentile(gofs_alt, 90), max(data_ref, data_alt)*1.05)
    ax.set_xlim(0, x_lim)
    xlab = r"$-2log(\lambda)$"
    ax.set_xlabel(xlab , x=1, ha='right')
    ax.set_ylabel("Pseudoexperiments", y=1, ha='right')

    if savename is not None:
        fig.savefig('{}.pdf'.format(savename), dpi=300, transparent=True, bbox_inches='tight')


if __name__ == '__main__':

    year = "2016"
    thisdir = os.getcwd()
    if "2016APV" in thisdir:
        year = "2016 APV"
    elif "2017" in thisdir:
        year = "2017"
    elif "2018" in thisdir:
        year = "2018"

    #Get data_ref
    infile1 = r.TFile.Open("baseline_obs.root")
    tree1= infile1.Get("limit")
    tree1.GetEntry(0)
    data_ref = getattr(tree1,"limit")

    #get data_alt
    infile2 = r.TFile.Open("alternative_obs.root")
    tree2 = infile2.Get("limit")
    tree2.GetEntry(0)
    data_alt = getattr(tree2,"limit")

    print("Baseline GoF: ", data_ref)
    print("Alternative GoF: ", data_alt)

    