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
singularity exec -B ${PWD}:/srv -B $pkl_dir --pwd /srv /cvmfs/unpacked.cern.ch/registry.hub.docker.com/coffeateam/coffea-dask:latest python make_hists.py $1

# Produce combine cards
conda run -n combine --no-capture-output python make_cards.py $1 > out_make_cards.txt

# Run the combine jobs
cd $1

mkdir -p plots

ln -s -f ../year_scripts/*.C .
ln -s -f ../year_scripts/*.sh .

conda run -n combine --no-capture-output ./make_workspace.sh > out_make_workspace.txt
conda run -n combine --no-capture-output ./exp_shapes.sh $2 > out_exp_shapes.txt 
conda run -n combine --no-capture-output ./exp_significance.sh $2 > significance.txt 

#Significance for VV as well
conda run -n combine --no-capture-output ./exp_significance_VV.sh $2 > significance_VV.txt 

# Produce the relevant plots
conda run -n combine --no-capture-output root -b -q draw_DataFit.C

if [ "$2" == "unblind" ]; then
    conda run -n plot --no-capture-output combine_postfits -i fitDiagnosticsTest.root -o plots/test_plot --data --style ../files/style_D.yml --onto qcd --sigs VH --bkgs QCD,qcd,ttbar,singlet,WjetsQQ,Zjets,Zjetsbb,VV,H,WLNu  --rmap 'VH:rVH' --project-signals 3 --xlabel 'Jet 1 $m_{SD}$ [GeV]' -p 
else
    conda run -n plot --no-capture-output combine_postfits -i fitDiagnosticsTest.root -o plots/test_plot --MC --style ../files/style_D.yml --onto qcd --sigs VH --bkgs QCD,qcd,ttbar,singlet,WjetsQQ,Zjets,Zjetsbb,VV,H,WLNu  --rmap 'VH:rVH' --project-signals 3 --xlabel 'Jet 1 $m_{SD}$ [GeV]' -p 
fi

cd ../