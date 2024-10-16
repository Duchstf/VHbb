import ROOT
import matplotlib.pyplot as plt
from matplotlib.pyplot import cm
import mplhep as hep
plt.style.use(hep.style.ROOT)

import matplotlib.pylab as pylab
params = {'legend.fontsize': 'small',
         'axes.labelsize': 'x-large',
         'axes.titlesize':'x-large',
         'xtick.labelsize':'medium',
         'ytick.labelsize':'medium'}
pylab.rcParams.update(params)

f = ROOT.TFile.Open('regions.root')
h = f.Get('Vmass_1_pass_VbbVqq_nominal')
h_up = f.Get('Vmass_1_pass_VbbVqq_PDF_weightUp')
h_down = f.Get('Vmass_1_pass_VbbVqq_PDF_weightDown')

def get_bin(h):

    bin_centers = []
    sumw = []
    error = []

    for i in range(1, h.GetNbinsX()+1):
        bin_centers += [h.GetBinCenter(i)]
        sumw += [h.GetBinContent(i)]
        error += [h.GetBinError(i)]

    return bin_centers, sumw, error


centers, nominal_y, nominal_err = get_bin(h)
_, up_y, up_err = get_bin(h_up)
_, down_y, down_err = get_bin(h_down)

plt.errorbar(centers, up_y,  yerr=up_err, fmt='o', markersize=10, label='Up')
plt.errorbar(centers, down_y,  yerr=down_err, fmt='o', markersize=10, label='Down')
plt.errorbar(centers, nominal_y,  yerr=nominal_err, fmt='o', markersize=10, label='Nominal')
plt.xlabel(r'$m_{SD}$ [GeV]')
plt.ylabel('Events')
plt.legend(fontsize=15)
plt.savefig('VbbVqq_Overlay.png', bbox_inches='tight')