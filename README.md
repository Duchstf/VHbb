# VHbb
Analysis framework for VHbb analysis

## Environment set up
You can set up the environment by following the instructions here: https://github.com/CoffeaTeam/lpcjobqueue/

After setting it up you could do `./shell` to set up the environment.

## How to run dask jobs

Log in with ssh tunneling:

```
ssh -L 8787:localhost:8787 dhoang@cmslpc173.fnal.gov
```

Renew your grid certificate:

```
grid-proxy-init -valid 1000:00
```

Run the job submssion script:

```
python submit-dask.py 2017 > dask.out 2>&1
```