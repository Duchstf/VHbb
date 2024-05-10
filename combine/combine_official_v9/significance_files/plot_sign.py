import os, subprocess
import numpy as np
import pandas as pd

#Plot settings
import matplotlib.pyplot as plt
import mplhep as hep
plt.style.use(hep.style.CMS)

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

#Open one file and extract the thresholds and significance
def open_file_and_extract(file_path):
    
    threshold = [float(file_path.split("_")[1][:-4])]
    significance = []
    status = False
    
    with open(file_path) as f:
        lines = f.read().splitlines()
        
    for x in lines:
            
        if x.startswith('Significance:'): significance.append(float(x[14:]))
        if "Minimization success! status=0" in x: status = True
    
    # print("Threshold: {}. Length: {}".format(threshold,len(threshold)))
    # print("Significance: ", significance)
    # print("Status: {}".format(status))
        
    if status: return threshold, significance
    else: return threshold, [0]
    

def scan_logs_out(log_dir):
    
    qcd2_thres = []
    all_sign = []
    
    #Loop over the files
    for file in os.listdir(log_dir):
        
        filename = os.fsdecode(file)
        if filename.endswith(".txt"):
            local_thres, local_sign = open_file_and_extract(os.path.join(log_dir,filename))
            
            if len(local_sign) > 0:
                    qcd2_thres += [x for x in local_thres]
                    all_sign += local_sign
    
    qcd2_thres = np.asarray(qcd2_thres)
    all_sign = np.asarray(all_sign)

    sorted_index = np.argsort(qcd2_thres) 
    plt.scatter(qcd2_thres[sorted_index][5:], all_sign[sorted_index][5:])
    plt.xlabel(r"V $PN_{MD}^{QCD}$ Cut")
    plt.ylabel(r"2017 Significance ($\sigma$)")
    plt.savefig("scan.pdf", bbox_inches='tight')
    
    print("Max Signifiance: ", max(all_sign))
    print("QCD Threshold: ", qcd2_thres[np.argmax(np.asarray(all_sign))])

    d = {'QCD2': np.asarray(qcd2_thres), 'significance':np.asarray(all_sign)}
    df = pd.DataFrame(data=d)
    
    df_print = df[(df['significance'] > 1.09)]

    for i in range(len(df_print)):
        print("---------")
        print("QCD2: ",df_print.iloc[i]['QCD2'])
        print("Significance: ", df_print.iloc[i]['significance'])

scan_logs_out("./")