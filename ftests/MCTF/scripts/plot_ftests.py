import os
import math
import numpy as np
import ROOT
import matplotlib.pyplot as plt
import mplhep as hep
plt.style.use(hep.style.ROOT)
from scipy.stats import f
#fig, ax = plt.subplots(1, 1)

nbins=23*6

def Ftest(lambda1,lambda2,p1,p2,nbins):
    '''
    Compare the goodness of fit between the two models
    '''
    with np.errstate(divide='ignore'):
        numerator = -2.0 * np.log(float(lambda1) / float(lambda2)) / float(p2 - p1)
        denominator = -2.0 * np.log(float(lambda2)) / float(nbins - p2)
        return numerator / denominator

if __name__ == '__main__':

    year = "2016"
    thisdir = os.getcwd()
    if "2016APV" in thisdir:
        year = "2016 APV"
    elif "2017" in thisdir:
        year = "2017"
    elif "2018" in thisdir:
        year = "2018"

    thisdir = os.getcwd().split("/")[-1]
    baseline = thisdir.split("_vs_")[0]
    alt = thisdir.split("_vs_")[1]

    pt1 = int(baseline.split("rho")[0].split("pt")[1])
    rho1 = int(baseline.split("rho")[1])
    p1 = (rho1+1)*(pt1+1)
    print("pt1: {}, rho1: {}, p1: {}".format(pt1, rho1, p1))

    pt2 = int(alt.split("rho")[0].split("pt")[1])
    rho2 = int(alt.split("rho")[1])
    p2 = (rho2+1)*(pt2+1)
    print("pt2: {}, rho2: {}, p2: {}".format(pt2, rho2, p2))

    lambda1_toys = []
    lambda2_toys = []

    seeds = [123487,123587,123687,123787,123887,123987,124087,124187,124287,124387]
    for s in seeds:

        # baseline gof                                                                                                 
        infile1 = ROOT.TFile.Open("higgsCombineToys.baseline.GoodnessOfFit.mH125."+str(s)+".root")
        tree1= infile1.Get("limit")
        for j in range(tree1.GetEntries()):
            tree1.GetEntry(j)
            lambda1_toys += [getattr(tree1,"limit")]

        # alternative gof
        infile2 = ROOT.TFile.Open("higgsCombineToys.alternative.GoodnessOfFit.mH125."+str(s)+".root")
        tree2 = infile2.Get("limit")
        for j in range(tree2.GetEntries()):
            tree2.GetEntry(j)
            lambda2_toys +=[getattr(tree2,"limit")]

    # Caculate the F-test for toys
    f_dist = [Ftest(lambda1_toys[j],lambda2_toys[j],p1,p2,nbins=nbins) for j in range(len(lambda1_toys))]
    print(f_dist)

    # Observed
    infile1 = ROOT.TFile.Open("baseline_obs.root")
    tree1= infile1.Get("limit")
    tree1.GetEntry(0)
    lambda1_obs = getattr(tree1,"limit")

    infile2 = ROOT.TFile.Open("alternative_obs.root")
    tree2 = infile2.Get("limit")
    tree2.GetEntry(0)
    lambda2_obs = getattr(tree2,"limit")

    print(lambda1_obs,lambda2_obs)
    f_obs = Ftest(lambda1_obs,lambda2_obs,p1,p2,nbins=nbins)
    print(f_obs)

    ntoys_good = len([y for y in f_dist if y>0])
    pvalue = 1.0*len([y for y in f_dist if y>f_obs])/ntoys_good
    print(pvalue)
    
    # maxval = max(np.max(f_dist),f_obs)+1
    maxval = 30

    ashist = plt.hist(f_dist,bins=np.linspace(0,maxval,25),histtype='step',color='black')
    ymax = 1.2*max(ashist[0])

    #Add Results
    baseline_order = [int(char) for char in baseline if char in '0123']
    baseline_label = 'TF({},{})'.format(baseline_order[0], baseline_order[1])

    alt_order = [int(char) for char in alt if char in '0123']
    alt_label = 'TF({},{})'.format(alt_order[0], alt_order[1])
    plt.plot([],[], color ='none', label=baseline_label + " vs. " + alt_label)
    plt.plot([],[], color = 'none', label="p-value = {:.2f}".format(pvalue))

    plt.errorbar((ashist[1][:-1]+ashist[1][1:])/2., ashist[0], yerr=np.sqrt(ashist[0]),linestyle='',color='black',marker='o',label= "Toys, N = {}".format(ntoys_good))
    plt.plot([f_obs,f_obs],[0,ymax],color='red',label="Observed = {:.2f}".format(f_obs))
    plt.ylim(0,ymax)

    x = np.linspace(0,maxval,250)
    plt.plot(x, ntoys_good*0.2*f.pdf(x, p2-p1, nbins-p2),color='blue', label='F pdf')

    hep.cms.label('Preliminary', data=True, year=year)  
    plt.legend(loc='best',frameon=True)
    plt.ylabel("Pseudo-experiments")
    plt.xlabel("F-statistic")

    plt.savefig(thisdir+".png",bbox_inches='tight')
    plt.savefig(thisdir+".pdf",bbox_inches='tight')