"""
Plot the TFs in each year

python plot_TFs.py <year>
"""

import numpy as np
import math

import matplotlib.pyplot as plt
import mplhep as hep
import sys


# Benstein polynomial calculation
def bern_elem(x, v, n):
    # Bernstein element calculation
    normalization = 1.0 * math.factorial(n) / (math.factorial(v) * math.factorial(n - v))
    Bvn = normalization * (x**v) * (1 - x) ** (n - v)
    return float(Bvn)


def TF(pT, rho, par_map=np.ones((1, 1)), n_rho=0, n_pT=0):
    # Calculate TF Polynomial for (n_pT, n_rho) degree Bernstein poly
    val = 0
    for i_pT in range(0, n_pT + 1):
        for i_rho in range(0, n_rho + 1):
            val += bern_elem(pT, i_pT, n_pT) * bern_elem(rho, i_rho, n_rho) * par_map[i_pT][i_rho]

    return val

# Check if there are enough arguments
if len(sys.argv) < 2:
    print("Usage: make_cards.py <year>")

# Setting different years depending on the input
global year
year = sys.argv[1]

