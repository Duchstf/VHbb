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

sample = "root://cmsxrootd-site.fnal.gov//store/mc/RunIISummer20UL17NanoAODv9/WZTo4Q_4f_TuneCP5_13TeV-amcatnloFXFX-madspin-pythia8/NANOAODSIM/106X_mc2017_realistic_v9-v2/130000/53E388A3-B5F6-104E-BECE-DDD5EA92C72E.root"
events = NanoEventsFactory.from_root(sample, schemaclass=NanoAODSchema).events()

print(dir(events))

print(events.fields)