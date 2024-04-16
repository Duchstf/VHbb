import numpy as np
import os

qcd2_scan_list = " ".join([str(round(x,4)) for x in list(np.linspace(0.,1.,500))])

scan_file = open("run_QCD_scan.sh","r+")
for line in scan_file:
        if 'THRES_LIST' in line:
            line=line.replace('THRES_LIST', qcd2_scan_list)
            scan_file.write(line)
        # print(line)
scan_file.close()
    
    
