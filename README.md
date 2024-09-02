# VHbb
Analysis framework for VHbb analysis


<img src="https://github.com/user-attachments/assets/3c43623f-6a2c-4cc0-ab7d-9013d2eec666" alt="image" width="300"/>


## Documentation
* Twiki: https://twiki.cern.ch/twiki/bin/view/CMSPublic/BoostedVqqHbbRun2
* iCMS upload link: https://cms.cern.ch/iCMS/
* iCMS AN Document Server: https://icms.cern.ch/tools/publications/notes/entries/AN/2022
* CADI: https://cms.cern.ch/iCMS/analysisadmin/cadilines?awg=any&awgyear=2024
* Pubtalk: https://cms-pub-talk.web.cern.ch/c/hig/hig-24-017/640

## References

### Talks
* [Booosted Z'+jets scale factors](https://indico.cern.ch/event/1355112/#16-booosted-zjets-scale-factor)
* [ParticleNet talk and corresponding paper](https://indico.physics.lbl.gov/event/975/contributions/8301/attachments/4047/5437/23.07.31_BOOST_Xbbcc_performance_CL.pdf)
* [Di-Higgs -> 4b approval talk.](https://indico.cern.ch/event/1078870/contributions/4537934/attachments/2313106/3947040/Preapproval_HH4bggF_280921.pdf)
* [Jennet's talk on VBF/ggF](https://indico.physics.lbl.gov/event/975/contributions/8306/attachments/4062/5457/Dickinson_BOOST23_CMSVBF_vf.pdf)

### Papers
* [ParticleNet BTV Paper](https://cds.cern.ch/record/2866276/files/BTV-22-001-pas.pdf)
* [ATLAS VH](https://arxiv.org/abs/2312.07605), [PRL Paper](https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.132.131802)
* [Electroweak Restoration at the LHC and Beyond: The Vh Channel](https://arxiv.org/abs/2012.00774)
* [A portrait of the Higgs boson by the CMS experiment ten years after the discovery]( https://www.nature.com/articles/s41586-022-04892-x)

### Other relevant links
* [Z' twiki](https://twiki.cern.ch/twiki/bin/edit/CMS/EXO24007)
* [Combine installation](https://cms-analysis.github.io/HiggsAnalysis-CombinedLimit/latest/)
* [NanoAOD attributes](https://cms-nanoaod-integration.web.cern.ch/integration/cms-swCMSSW_12_4_X/mc123Xrun3_v10_doc.html)
* [Save data array to ParQuet](https://awkward-array.org/doc/main/reference/generated/ak.to_parquet.html)
* [BTV Citation list](https://btv-wiki.docs.cern.ch/PerformanceCalibration/Citations/)

----
## Environment set up
You can set up the environment by following the instructions here: https://github.com/CoffeaTeam/lpcjobqueue/

After setting it up you could do `./shell` to set up the environment.

## How to run dask jobs

Log in with ssh tunneling:

```
ssh -L 8787:localhost:8787 dhoang@cmslpc138.fnal.gov
```

Renew your grid certificate:

```
grid-proxy-init -valid 1000:00
```

Run the `./shell` script as setup above:

```
./shell
```

**Note:** View all coffea images: 
```
ls /cvmfs/unpacked.cern.ch/registry.hub.docker.com/coffeateam/
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
ssh -L 127.0.0.1:8703:127.0.0.1:8703 dhoang@cmslpc327.fnal.gov
```

```
jupyter notebook --no-browser --port 8703 --ip 127.0.0.1
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

## Bias Test
* Following example from here: https://github.com/andrzejnovak/higgstocharm?tab=readme-ov-file#running-bias-tests
* Tests done using combine v10

```
for bias in 0 1 `seq 5 5 100`
    do
    combineTool.py -M FitDiagnostics --expectSignal $bias -n bias$bias -d model_combined.root --cminDefaultMinimizerStrategy 0 --robustFit=1 -t 20 -s 1:50:1 --job-mode condor --sub-opts='+JobFlavour = "workday"' --task-name ggHcc$bias
    done
```

```
for bias in 0 1 `seq 5 5 100`
    do 
    hadd -f bias$bias.root *Combinebias$bias.*
    done
```




