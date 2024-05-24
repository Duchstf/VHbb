#Try submitting stuff several times
# ssh -L 8787:localhost:8787 dhoang@cmslpc325.fnal.gov
# ./submit_jobs.sh 2016APV
year=$1
python submit/submit_muonCR.py $year > dask.out 2>&1
python submit/submit_muonCR.py $year > dask.out 2>&1
python submit/submit_muonCR.py $year > dask.out 2>&1
python submit/submit_muonCR.py $year > dask.out 2>&1
python submit/submit_muonCR.py $year > dask.out 2>&1

