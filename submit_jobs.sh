#Try submitting stuff several times
# ssh -L 8787:localhost:8787 dhoang@cmslpc342.fnal.gov
# ./submit_jobs.sh 2018 > dask.out 2>&1
year=$1
python submit/submit-official.py $year 
python submit/submit-official.py $year
python submit/submit-official.py $year
