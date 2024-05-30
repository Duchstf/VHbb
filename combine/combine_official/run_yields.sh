#!/bin/bash

#! WARNING: you eed to create the year's directory and include the pickle file first!
#EXAMPLE: ./run_CombineSingle.sh 2016

# Check if no arguments were provided
if [ $# -eq 0 ]; then
    echo "Error: No year provided."
    exit 1
fi

if [ -d $1 ]; then
    echo "$1 directory exists. Starting cleaning."
else
    echo "$1 directory does not exists. Making dir ... "
    mkdir -p $1
fi

pkl_dir="/uscms_data/d3/dhoang/VH_analysis/CMSSW_10_2_13/src/VHbb/output/pickle"

#Define the pickling directory
signal_pkl="$pkl_dir/vhbb_official/$1/h.pkl"
muonCR_pkl="$pkl_dir/muonCR/$1/h.pkl"
theory_systematics_pkl="$pkl_dir/vhbb_theory_systematics/$1/h.pkl"

# Clean everything except for the pickle file
cd $1

# Remove files and symbolic links that don't match the patterns
find . -maxdepth 1 \( -type f -o -type l \) -exec rm -f {} \;
rm -rf plots
rm -rf output

#Symbolic linking the pickle files to save space
ln -s ${signal_pkl} signal.pkl
ln -s ${muonCR_pkl} muonCR.pkl
ln -s ${theory_systematics_pkl} theory_syst.pkl

#Return to the main directory
cd ..

echo "finish cleaning and symbolic linking"

#Make the histograms
singularity exec -B ${PWD}:/srv -B $pkl_dir --pwd /srv /cvmfs/unpacked.cern.ch/registry.hub.docker.com/coffeateam/coffea-dask:latest python make_yields.py $1 > out$1.test
