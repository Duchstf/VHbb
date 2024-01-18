singularity exec -B ${PWD}:/srv --pwd /srv /cvmfs/unpacked.cern.ch/registry.hub.docker.com/coffeateam/coffea-dask:latest python make_hists.py $1
