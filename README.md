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
python submit/submit-dask.py 2017 > dask.out 2>&1
```

or to run a selected sample (define the selected sample in the script):

```
python submit/submit-dask-selected.py 2017 > dask.out 2>&1
```

## Run Jupyter Notebooks

```
ssh -L 127.0.0.1:8703:127.0.0.1:8703 dhoang@cmslpc153.fnal.gov
```

```
jupyter nbclassic --no-browser --port 8703 --ip 127.0.0.1
```

## Conda environment

```
conda-env create -f environment.yml
```

Activate the environment:

```
conda activate vhbb
```

And then do whatever you want in this environment (edit files, open notebooks, etc.). To deactivate the environment:

```
conda deactivate
```

If you make any update for the environment, please edit the `environment.yml` file and run:

```
conda env update --file environment.yml  --prune
```

# References

## Talks

* ParticleNet talk and corresponding paper: https://indico.physics.lbl.gov/event/975/contributions/8301/attachments/4047/5437/23.07.31_BOOST_Xbbcc_performance_CL.pdf
* [Di-Higgs -> 4b approval talk.](https://indico.cern.ch/event/1078870/contributions/4537934/attachments/2313106/3947040/Preapproval_HH4bggF_280921.pdf)
* Jennet's talk on VBF/ggF: https://indico.physics.lbl.gov/event/975/contributions/8306/attachments/4062/5457/Dickinson_BOOST23_CMSVBF_vf.pdf

## Papers
* **[Electroweak Restoration at the LHC and Beyond: The Vh Channel](https://arxiv.org/abs/2012.00774)**
* A portrait of the Higgs boson by the CMS experiment ten years after the discovery: https://www.nature.com/articles/s41586-022-04892-x
* ParticleNet Performance Paper: https://cds.cern.ch/record/2866276/files/BTV-22-001-pas.pdf

## Other relevant links
* [NanoAOD attributes](https://cms-nanoaod-integration.web.cern.ch/integration/master-cmsswmaster/mc102X_doc.html)
* [Save data array to ParQuet](https://awkward-array.org/doc/main/reference/generated/ak.to_parquet.html)
