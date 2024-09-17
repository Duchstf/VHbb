'''
Processor for DDT Maps

ssh -L 8787:localhost:8787 dhoang@cmslpc325.fnal.gov
grid-proxy-init -valid 10000:00

./shell

And then

python submit/submit_DDT.py $year > dask.out 2>&1
'''

import utils, sys 

# Add path so the script sees the modules in parent directory
sys.path.append('/srv')

from boostedhiggs import DDT
tag = "DDT"
year = sys.argv[1]
target_list = ['QCD']
processor = DDT(year=year)

utils.submit_processor(year, tag, processor, '2GB', target_list=target_list)