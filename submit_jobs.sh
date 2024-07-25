#Try submitting stuff several times
# ssh -L 8787:localhost:8787 dhoang@cmslpc325.fnal.gov
# ./submit_jobs.sh 2016 > dask.out 2>&1
year=$1
python submit/submit_official_TheorySys.py $year
