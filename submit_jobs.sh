#Try submitting stuff several times
# ssh -L 8787:localhost:8787 dhoang@cmslpc325.fnal.gov
# ./submit_jobs.sh 2018 > dask.out 2>&1
year=$1
python submit/submit-HEM.py $year
python submit/submit-HEM.py $year
