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
    echo "$1 directory does not exists."
    exit 1
fi

#Just to tie the path for the symbolic link to work
pkl_dir="/uscms_data/d3/dhoang/VH_analysis/CMSSW_10_2_13/src/VHbb/output/pickle"
signal_pkl="$pkl_dir/vhbb_PNQCDScan/$1/h.pkl"

echo $signal_pkl

# Clean everything except for the pickle file
cd $1

# Remove files and symbolic links that don't match the patterns
find . -maxdepth 1 \( -type f -o -type l \) -exec rm -f {} \;
rm -rf plots
rm -rf output

ln -s ${signal_pkl} signal.pkl

cd ..

echo "finish cleaning and symbolic linking"

#Define the pickling directory
signal_pkl="$pkl_dir/vhbb_PNQCDScan/$1/h.pkl"

#Insert the qcd threshold into make hists
sed -i "s/QCD2_THRES =.*/QCD2_THRES = $2/g" make_hists.py 

#Make the histograms
singularity exec -B ${PWD}:/srv -B $pkl_dir --pwd /srv /cvmfs/unpacked.cern.ch/registry.hub.docker.com/coffeateam/coffea-dask:latest python make_hists.py $1 > out_make_hists.txt
conda run -n combine --no-capture-output python make_cards.py $1 > out_make_cards.txt #Run combine cards

#Run the combine jobs
cd $1
ln -s -f ../year_scripts/*.sh .

conda run -n combine --no-capture-output ./make_workspace.sh > out_make_workspace.txt
conda run -n combine --no-capture-output ./exp_significance.sh > ../significance_files_$1/significance_$2.txt

cd ../

