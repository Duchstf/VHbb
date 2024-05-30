import json
import sys
import matplotlib.pyplot as plt
from matplotlib.pyplot import cm
import mplhep as hep
plt.style.use(hep.style.ROOT)

import matplotlib.pylab as pylab
params = {'legend.fontsize': 'medium',
         'axes.labelsize': 'x-large',
         'axes.titlesize':'x-large',
         'xtick.labelsize':'medium',
         'ytick.labelsize':'medium'}
pylab.rcParams.update(params)

#line thickness
# import matplotlib as mpl
# mpl.rcParams['lines.linewidth'] = 5

from coffea import hist
import pickle

import numpy as np

#Dataset parameters
lumis = {}
lumis['2016'] = 16.81
lumis['2016APV'] = 19.52
lumis['2017'] = 41.5
lumis['2018'] = 59.9

