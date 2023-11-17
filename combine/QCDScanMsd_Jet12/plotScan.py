import numpy as np
import matplotlib.pyplot as plt
import mplhep as hep
plt.style.use(hep.style.CMS)

#Define the cut list and significance value
temp = [round(x,2) for x in list(np.linspace(0,1,21))]
QCD_cut_list = temp[1:]
sign_list = [0.654394, 0.65329, 0.645094, 0.629655, 0.633363, 0.622014, 0.61536, 0.613218, 0.607723, 0.604938, 0.603315, 0.601244, 0.600033, 0.597807, 0.595911, 0.593088, 0.590539, 0.58755, 0.586062, 0.585035]

#plot
plt.plot(QCD_cut_list, sign_list, '-o', markersize=13)
plt.plot([],[], 'none', label='(bb,cc) = (HP, LP)')
plt.legend()
plt.xlabel('Jet 2 QCD < X')
plt.ylabel(r'Significance $\sigma$')
plt.show()
plt.savefig('QCDScan.pdf')
plt.savefig('QCDScan.png')