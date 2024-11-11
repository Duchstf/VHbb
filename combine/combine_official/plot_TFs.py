"""
Plot the TFs in each year

python plot_TFs.py <year>
"""

import numpy as np
import math

import matplotlib.pyplot as plt
import mplhep as hep
import sys
import uproot
hep.style.use("CMS")  # Optional if you want to use CMS style from mplhep


ptbins = np.array([450, 1200])
msdbins = np.linspace(40, 201, 24)
n_ptbins = ptbins.shape[0] - 1
ptpts, msdpts = np.meshgrid(ptbins[:-1] + 0.3 * np.diff(ptbins), msdbins[:-1] + 0.5 * np.diff(msdbins), indexing="ij")
rhopts = 2 * np.log(msdpts / ptpts)
ptscaled = (ptpts - 450.0) / (1200.0 - 450.0)
rhoscaled = (rhopts - (-6)) / ((-2.1) - (-6))

TF_res_values={
    "2016": np.asarray([[9.8567e-01]]),
    "2016APV": np.asarray([[8.8771e-01, 1.5779]]),
    "2017": np.asarray([[1.1449]]),
    "2018": np.asarray([[0.65979, 2.0764]])
}

# Benstein polynomial calculation
def bern_elem(x, v, n):
    # Bernstein element calculation
    normalization = 1.0 * math.factorial(n) / (math.factorial(v) * math.factorial(n - v))
    Bvn = normalization * (x**v) * (1 - x) ** (n - v)
    return Bvn


def TF(pT, rho, par_map=np.ones((1, 1)), n_rho=0, n_pT=0):
    # Calculate TF Polynomial for (n_pT, n_rho) degree Bernstein poly
    val = 0
    for i_pT in range(0, n_pT + 1):
        for i_rho in range(0, n_rho + 1):
            val += bern_elem(pT, i_pT, n_pT) * bern_elem(rho, i_rho, n_rho) * par_map[i_pT][i_rho]

    return val

def plot_TFres_values(year):

    par_map = TF_res_values[year]
    
    # Calculate TF values
    TF_array = TF(pT=ptscaled, rho=rhoscaled, par_map=par_map, n_rho=len(par_map[0]) - 1, n_pT=0)
    
    # Flatten the TF array to match the rhoscaled bins
    TF_array = TF_array.flatten()

    # Calculate midpoints of msdbins for plotting
    # Calculate midpoints of msdbins
    msd_midpoints = (msdbins[:-1] + msdbins[1:]) / 2

    # Plot the TF values against rho midpoints
    plt.figure(figsize=(8, 6))
    plt.plot(msd_midpoints, TF_array, marker='o', linestyle='-', label=r'$\rho$ order: {}'.format(len(par_map[0]) - 1))
    plt.xlabel(r'$m_{SD}$ [GeV] ')
    plt.ylabel(r'Post-fit $TF_{res}$ ' + f"({year})")
    plt.legend()
    plt.grid(True)
    plt.savefig(f"plots/TFres_{year}.pdf",bbox_inches='tight')

# Check if there are enough arguments
if len(sys.argv) < 2:
    print("Usage: make_cards.py <year>")

# Setting different years depending on the input
global year
year = sys.argv[1]

plot_TFres_values(year)
