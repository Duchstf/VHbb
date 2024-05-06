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
    echo "$1 directory does not exists. Please create the symbolic link."
    exit 1
fi

pkl_dir="/uscms_data/d3/dhoang/VH_analysis/CMSSW_10_2_13/src/VHbb/output/pickle"

#Define the pickling directory
signal_pkl="$pkl_dir/vhbb_v11/$1/ParticleNet_msd.pkl"
muonCR_pkl="$pkl_dir/muonCR/$1/h.pkl"

# Clean everything except for the pickle file
cd $1

# Remove files and symbolic links that don't match the patterns
find . -maxdepth 1 \( -type f -o -type l \) -exec rm -f {} \;
rm -rf plots
rm -rf output

#Symbolic linking the pickle files to save space
ln -s ${signal_pkl} .
ln -s ${muonCR_pkl} .

#Return to the main directory
cd ..

echo "finish cleaning and symbolic linking"

#Make the histograms
singularity exec -B ${PWD}:/srv -B $pkl_dir --pwd /srv /cvmfs/unpacked.cern.ch/registry.hub.docker.com/coffeateam/coffea-dask:latest python make_hists.py $1

#Activate the environment
# cmsenv

# #Produce combine cards
# python make_cards.py $1 > out_make_cards.txt

# #Run the combine jobs
# cd $1

# mkdir -p plots

# ln -s -f ../year_scripts/*.C .
# ln -s -f ../year_scripts/*.sh .

# ./make_workspace.sh

# # ./exp_shapes_VV.sh 
# # ./exp_significance_VV.sh > significance_VV.txt

# ./exp_shapes.sh 
# ./exp_significance.sh > significance.txt

# # #Produce the relevant plots
# root -b -q draw_DataFit.C

# combine_postfits -i fitDiagnostics.root -o plots/test_plot --MC --style ../files/style_D.yml --onto qcd --sigs VH --bkgs qcd,ttbar,singlet,WjetsQQ,Zjets,Zjetsbb,VV,H  --rmap 'VH:rVH' --project-signals 3 --xlabel 'Jet 1 $m_{SD}$ [GeV]' -p

# cd ../