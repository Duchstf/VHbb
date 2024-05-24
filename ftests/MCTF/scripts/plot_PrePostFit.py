import os,sys
import argparse
import numpy as np
import matplotlib
matplotlib.use("Agg")
import uproot
import matplotlib.pyplot as plt
import hist
import mplhep as hep
plt.style.use(hep.style.ROOT)
import matplotlib.transforms as transforms

def prepostplot(data, data_errors_low, data_errors_high, prefit_qcd, postfit_qcd, bins, centers, degs=(1,2), year='2016', chi2=None, reg=None, savename=None):
    width = (bins[1] - bins[0]) / 2
    
    fig, (ax, subax) = plt.subplots(2, 1, gridspec_kw={'height_ratios': [3, 1]}, sharex=True)
    fig.subplots_adjust(hspace=0)
    ax.set_xlim(40, 201)

    if chi2 is None:
        with np.errstate(divide='ignore'):
            chi2_pre = np.sum(np.nan_to_num((data-prefit_qcd)**2/prefit_qcd, 0))
            chi2_post = np.sum(np.nan_to_num((data-postfit_qcd)**2/prefit_qcd, 0))
    else:
        chi2_pre, chi2_post = chi2
    
    # Plot
    hep.histplot(prefit_qcd, bins, color='red', linestyle="--", ax=ax,
                 label='PreFit, $\chi^2 = {:.1f}$'.format(chi2_pre))
    hep.histplot(postfit_qcd, bins, color='blue', ax=ax, 
                 label='PostFit, $\chi^2 = {:.1f}$'.format(chi2_post))
    ax.errorbar(centers, data, fmt='o', xerr=width, yerr=[data_errors_low, data_errors_high], color='black', label='True QCD')
    
    leg = ax.legend(title=(reg+"\n" if reg is not None else "") + "TF({},{})".format(degs[0], degs[1]))
    plt.setp(leg.get_title(), multialignment='center')
    hep.cms.label(data=False, year=year, ax=ax)
    ax.set_ylabel("Events / 7GeV", y=1, ha='right')
    ax.set_yticks(ax.get_yticks()[1:])

    #Subplots
    subax.axhline(1, color='grey', ls='--')
    subax.errorbar(centers, (postfit_qcd/data),
                   fmt='o', xerr=width, color='blue')
    subax.axhline(1, color='grey', ls='--')
    eb = subax.errorbar(centers, (prefit_qcd/data),
                   fmt='o', xerr=width, color='red')
    eb[-1][0].set_linestyle('--')
    subax.set_ylim(0.5, 1.5)
    subax.set_ylabel('Pred/True')
    subax.set_xlabel('jet $m_{SD}$ [GeV]', x=1, ha='right')

    if savename is not None: 
        fig.savefig('{}.pdf'.format(savename), dpi=300, transparent=True, bbox_inches='tight')

def parse_data(fit_data, TreeName):

    binwidth = 7.0

    prefit_qcd = fit_data['shapes_prefit/{}/qcd'.format(TreeName)].values()*binwidth
    postfit_qcd = fit_data['shapes_fit_s/{}/qcd'.format(TreeName)].values()*binwidth

    #Take the data and bin centers
    data_hist = fit_data['shapes_fit_s/{}/data'.format(TreeName)]

    centers = data_hist.values()[0]
    data = data_hist.values()[1]*binwidth
    data_errors_low = data_hist.errors("low")[1]*binwidth
    data_errors_high = data_hist.errors("high")[1]*binwidth

    bins = fit_data['shapes_prefit/{}/qcd'.format(TreeName)].axis().edges()
    
    return data, data_errors_low, data_errors_high, prefit_qcd, postfit_qcd, bins, centers

if __name__ == "__main__":

    #Select year
    year = sys.argv[1]
    pass_regions = [f'VBin{i}pass{year}' for i in range(3)] # 3 V mass bins regions

    #Load the Fit Diagnostic File
    filepath = f'../{year}/pt0rho0/fitDiagnosticsTest.root'
    fit_data = uproot.open(filepath)
    
    for region in pass_regions:
        prepostplot(*parse_data(fit_data, region), degs=(0,0), reg=region, year=year, savename=f'plots/{region}')
    

