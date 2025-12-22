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

from boostedhiggs import TriggerProcessor as vhbb_processor
tag = "trigger_withbb"
year = sys.argv[1]
target_list = ["trigger"]

processor = vhbb_processor(year=year)
utils.submit_processor(year, tag, processor, '6GB', split_sample=False, target_list=target_list)