'''
To submit processing jobs, do:

ssh -L 8787:localhost:8787 dhoang@cmslpc325.fnal.gov

./shell

And then

python submit/submit_official_TheorySys.py 2017 > dask.out 2>&1
'''

import utils, sys 

# Add path so the script sees the modules in parent directory
sys.path.append('/srv')

from boostedhiggs import VHbbProcessorTheory as vhbb_processor
tag = "vhbb_theory"
syst = True
year = sys.argv[1]
target_list = ['ttH', 'ggF', 'VVNLO', 'VBFHToBBDipoleRecoilOn','ZH', 'WH'] #Sample to ignore processing
processor = vhbb_processor(year=year, jet_arbitration='T_bvq', systematics=syst)

utils.submit_processor(year, tag, processor, '4GB', target_list=target_list)