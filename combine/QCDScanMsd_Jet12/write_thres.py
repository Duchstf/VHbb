import numpy as np

QCD_thres_temp = [round(x,2) for x in list(np.linspace(0,0.5,51))] + [round(x,2) for x in list(np.linspace(0.6,1,5))]
QCD_thres = QCD_thres_temp[1:]

for thres in QCD_thres:
    
    qcd_scan_file = "run_QCD_scan.sh"
    print("Writing threshold to run QCD scan: ...")
    scan_file = open(qcd_scan_file,"w")
    for line in qcd_scan_file:
            line=line.replace('THRES_LIST', '"{}" '.format(QCD_thres))
            scan_file.write(line)
    scan_file.close()

