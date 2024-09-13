import awkward as ak
import uproot
import numpy as np
from coffea.nanoevents import NanoEventsFactory, NanoAODSchema

import matplotlib.pyplot as plt
import matplotlib.colors as colors
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
import matplotlib as mpl
mpl.rcParams['lines.linewidth'] = 5

sample = "root://cmsxrootd.fnal.gov//store/user/lpcpfnano/cmantill/v2_3/2017/HToBB/WminusH_HToBB_WToQQ_M-125_TuneCP5_13TeV-powheg-pythia8/WminusH_HToBB_WToQQ/230217_201146/0000/nano_mc2017_57.root"
events = NanoEventsFactory.from_root(sample, schemaclass=NanoAODSchema).events()