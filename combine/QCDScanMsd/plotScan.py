import numpy as np
import matplotlib.pyplot as plt
import mplhep as hep
plt.style.use(hep.style.CMS)

#Define the cut list and significance value
temp = [round(x,2) for x in list(np.linspace(0,1,21))]
QCD_cut_list = temp[1:]
sign_list = [0.35194, 0.347904, 0.332249, 0.303669, 0.308082, 0.28808, 0.278363, 0.273944, 0.265492, 0.261177, 0.257959, 0.254412, 0.252317, 0.248022, 0.244772, 0.239157, 0.234905, 0.230413, 0.228209, 0.226454]

#plot
plt.plot(QCD_cut_list, sign_list, '-o', markersize=13)
plt.plot([],[], 'none', label='(bb,cc) = (HP, LP)')
plt.legend()
plt.xlabel('Jet 2 QCD < X')
plt.ylabel(r'Significance $\sigma$')
plt.show()
plt.savefig('QCDScan.pdf')
plt.savefig('QCDScan.png')