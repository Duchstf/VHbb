import os,sys
import argparse
import numpy as np
import matplotlib
matplotlib.use("Agg")
import uproot
import matplotlib.pyplot as plt
import hist
import re
import mplhep as hep
plt.style.use(hep.style.ROOT)
import matplotlib.transforms as transforms

def prepostplot(data, data_errors_low, data_errors_high, prefit_qcd, postfit_qcd, bins, centers, degs=(1,2), year='2016', chi2=None, reg=None, savename=None):
    width = (bins[1] - bins[0]) / 2
    
    fig, (ax, subax) = plt.subplots(2, 1, gridspec_kw={'height_ratios': [3, 1]}, sharex=True)
    fig.subplots_adjust(hspace=0)
    ax.set_xlim(40, 201)

    prediction = postfit_qcd
    prediction_errors = np.sqrt(postfit_qcd)  # Assuming Poisson errors for prediction

    # Total uncertainty (data and prediction uncertainties combined)
    # Calculate data errors (average if asymmetric)
    data_errors = (data_errors_low + data_errors_high) / 2

    # Replace zeros in data_errors to avoid division by zero
    data_errors = np.where(data_errors == 0, 1e-10, data_errors)
    total_uncertainty = np.sqrt(data_errors**2 + prediction_errors**2)

    if chi2 is None:
        with np.errstate(divide='ignore'):
            chi2_pre = np.sum(np.nan_to_num((data-prefit_qcd)**2/total_uncertainty**2, 0))
            chi2_post = np.sum(np.nan_to_num((data-postfit_qcd)**2/total_uncertainty**2, 0))
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
    # Use postfit_qcd as the prediction
    prediction = postfit_qcd
    prediction_errors = np.sqrt(postfit_qcd)  # Assuming Poisson errors for prediction

    # Total uncertainty (data and prediction uncertainties combined)
    # Calculate data errors (average if asymmetric)
    data_errors = (data_errors_low + data_errors_high) / 2

    # Replace zeros in data_errors to avoid division by zero
    data_errors = np.where(data_errors == 0, 1e-10, data_errors)
    total_uncertainty = np.sqrt(data_errors**2 + prediction_errors**2)

    # Avoid division by zero in total_uncertainty
    total_uncertainty = np.where(total_uncertainty == 0, 1e-10, total_uncertainty)

    # Calculate residuals
    residuals = (data - prediction) / total_uncertainty

    # Uncertainty on residuals (should be 1)
    residuals_errors = np.ones_like(residuals)

    # Plot the residuals with error bars
    subax.errorbar(centers, residuals, yerr=residuals_errors, fmt='o', color='k', markersize=5)

    # Add shaded regions for ±1σ and ±2σ
    subax.axhline(0, color='grey', linestyle='--')
    subax.fill_between(bins, -1, 1, facecolor='yellow', alpha=0.3, step='post', label=r'$\pm1\sigma$')
    subax.fill_between(bins, -2, 2, facecolor='green', alpha=0.2, step='post', label=r'$\pm2\sigma$')

    subax.set_ylabel(r'$\frac{\text{data - pred}}{\text{unc}}$')
    subax.set_xlabel(r'Jet $m_{SD}$ [GeV]', x=1, ha='right')
    subax.set_xlim(ax.get_xlim())
    # Set y-limits based on the residuals
    residuals_max = np.nanmax(np.abs(residuals))
    subax.set_ylim(-max(3, residuals_max + 1), max(3, residuals_max + 1))

    # Add legend to the residuals plot
    subax.legend(loc='upper right')


    # subax.axhline(1, color='grey', ls='--')
    # subax.errorbar(centers, (postfit_qcd/data),
    #                fmt='o', xerr=width, color='blue')
    # subax.axhline(1, color='grey', ls='--')
    # eb = subax.errorbar(centers, (prefit_qcd/data),
    #                fmt='o', xerr=width, color='red')
    # eb[-1][0].set_linestyle('--')
    # subax.set_ylim(0.5, 1.5)
    # subax.set_ylabel('Pred/True')
    # subax.set_xlabel('jet $m_{SD}$ [GeV]', x=1, ha='right')

    if savename is not None: 
        fig.savefig('{}.pdf'.format(savename), dpi=300, transparent=True, bbox_inches='tight')
        fig.savefig('{}.png'.format(savename), dpi=300, transparent=True, bbox_inches='tight')

def parse_data(fit_data, TreeName):

    binwidth = 7.0

    prefit_qcd = fit_data['shapes_prefit/{}/qcd'.format(TreeName)].values()*binwidth
    postfit_qcd = fit_data['shapes_fit_s/{}/qcd'.format(TreeName)].values()*binwidth

    #Take the data and bin centers

    # Regular expression to match the desired components
    pattern = r'(\d+)([a-zA-Z]+)(\d+)'

    # Perform the search
    match = re.search(pattern, TreeName)

    if match:
        v_bin = int(match.group(1))   # First number
        xbb_region = match.group(2)   # String part
        year = int(match.group(3))  # Second number
    else:
        print("No match found.")

    region_file = f"../../../output/vhbb_official/{year}/regions.root"
    region_MC = uproot.open(region_file)
    QCD_string = f"Vmass_{v_bin}_{xbb_region}_QCD_nominal"
    QCD_hist = region_MC[QCD_string]

    values, edges = QCD_hist.to_numpy()  # Bin edges and bin values
    errors = QCD_hist.variances() ** 0.5 if QCD_hist.variances() is not None else None  # Bin errors (sqrt of variances)

    # Compute bin centers from edges
    bin_centers = (edges[:-1] + edges[1:]) / 2

    data_hist = fit_data['shapes_fit_s/{}/data'.format(TreeName)]

    centers = bin_centers
    data = values
    data_errors_low = errors
    data_errors_high = errors

    bins = fit_data['shapes_prefit/{}/qcd'.format(TreeName)].axis().edges()
    
    return data, data_errors_low, data_errors_high, prefit_qcd, postfit_qcd, bins, centers

if __name__ == "__main__":

    # Create the parser
    parser = argparse.ArgumentParser(description='Process some integers.')

    # Add the arguments
    parser.add_argument('--pt', type=int, default=0, help='The pt value')
    parser.add_argument('--rho', type=int, default=0, help='The rho value')
    parser.add_argument('--year', type=str, default="2016APV", help='The year value')

    # Parse the arguments
    args = parser.parse_args()

    # Access the arguments
    pt = args.pt
    rho = args.rho
    year = args.year

    #Select year
    pass_regions = [f'VBin{i}pass{year}' for i in range(3)] # 3 V mass bins regions

    #Load the Fit Diagnostic File
    filepath = f'../{year}/pt{pt}rho{rho}/fitDiagnosticsTest.root'
    fit_data = uproot.open(filepath)
    
    for region in pass_regions:
        prepostplot(*parse_data(fit_data, region), degs=(pt,rho), reg=region, year=year, savename=f'plots/{region}')
    

