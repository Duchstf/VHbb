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

Run the `./shell` script as setup above:

```
./shell coffeateam/coffea-dask:0.7.21-fastjet-3.4.0.1-g6238ea8
```

Run the job submssion script:

```
python submit-dask.py 2017 > dask.out 2>&1
```

# References

## Talks

* ParticleNet talk and corresponding paper: https://indico.physics.lbl.gov/event/975/contributions/8301/attachments/4047/5437/23.07.31_BOOST_Xbbcc_performance_CL.pdf
* [Di-Higgs -> 4b approval talk.](https://indico.cern.ch/event/1078870/contributions/4537934/attachments/2313106/3947040/Preapproval_HH4bggF_280921.pdf)https://indico.cern.ch/event/1078870/contributions/4537934/attachments/2313106/3947040/Preapproval_HH4bggF_280921.pdf 

## Papers

* ParticleNet Performance Paper: https://cds.cern.ch/record/2866276/files/BTV-22-001-pas.pdf 
