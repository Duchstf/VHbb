'''
To submit processing jobs, do:

ssh -L 8787:localhost:8787 dhoang@cmslpc325.fnal.gov
grid-proxy-init -valid 10000:00

./shell

And then

python submit/submit-official.py $year > dask.out 2>&1
'''

import utils, sys 

# Add path so the script sees the modules in parent directory
sys.path.append('/srv')

from boostedhiggs import VHbbProcessorOfficial as vhbb_processor
tag = "vhbb_official"
syst = True
year = sys.argv[1]
ignore_list = ['muondata','WLNu'] #Sample to ignore processing
# target_list = ['data', 'QCD']
processor = vhbb_processor(year=year, jet_arbitration='T_bvq', systematics=syst)

utils.submit_processor(year, tag, processor, '2GB', ignore_list=ignore_list)