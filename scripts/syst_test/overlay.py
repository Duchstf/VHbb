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

f0 = ROOT.TFile.Open('MinusOne.root')
f1 = ROOT.TFile.Open('PlusOne.root')
nominal = ROOT.TFile.Open('Zero.root')

def get_bin(f, bin=2):

    h = f.Get(f'shapes_fit_s/VBin{bin}pass2018/ZH')

    bin_centers = []
    sumw = []
    error = []

    for i in range(1, h.GetNbinsX()+1):
        bin_centers += [h.GetBinCenter(i)]
        sumw += [h.GetBinContent(i)]
        error += [h.GetBinError(i)]

    return bin_centers, sumw, error


centers, f0_y, f0_err = get_bin(f0)
_, f1_y, f1_err = get_bin(f1)
_, nominal_y, nominal_err = get_bin(nominal)

plt.errorbar(centers, f0_y,  yerr=f0_err, fmt='o', markersize=10, label='Vmass Bin 2, ZH, -1')
plt.errorbar(centers, f1_y,  yerr=f1_err, fmt='o', markersize=10, label='Vmass Bin 2, ZH, 1')
plt.errorbar(centers, nominal_y,  yerr=nominal_err, fmt='o', markersize=10, label='Vmass Bin 2, ZH, Nominal')
plt.xlabel(r'$m_{SD}$ [GeV]')
plt.ylabel('Events')
plt.legend(fontsize=15)
plt.savefig('Bin2_ZH_Overlay.png', bbox_inches='tight')

#Bin 1 as well
centers, f0_y, f0_err = get_bin(f0, bin=1)
_, f1_y, f1_err = get_bin(f1, bin=1)
_, nominal_y, nominal_err = get_bin(nominal, bin=1)

plt.figure()
plt.errorbar(centers, f0_y,  yerr=f0_err, fmt='o', markersize=10, label='Vmass Bin 1 (SR), ZH, -1')
plt.errorbar(centers, f1_y,  yerr=f1_err, fmt='o', markersize=10, label='Vmass Bin 1 (SR), ZH, 1')
plt.errorbar(centers, nominal_y,  yerr=nominal_err, fmt='o', markersize=10, label='Vmass Bin 1, ZH, Nominal')

plt.xlabel(r'$m_{SD}$ [GeV]')
plt.ylabel('Events')
plt.legend(fontsize=15)
plt.savefig('Bin1_ZH_Overlay.png', bbox_inches='tight')

