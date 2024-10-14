#!/bin/bash

#This script is used to derive the wTag CR templates from the data
#EXAMPLE: ./derive.sh 2016

# Check if no arguments were provided
if [ $# -eq 0 ]; then
    echo "Error: No year provided."
    exit 1
fi

year=$1

if [ -d templates/$year ]; then
    echo "$1 directory exists. Starting cleaning."
    cd templates/
    rm -rf $year
    cd ..
else
    echo "$1 directory does not exists. Making dir ... "
    mkdir -p templates/$year
fi

out_dir="/uscms_data/d3/dhoang/VH_analysis/CMSSW_10_2_13/src/VHbb/output/"
tnp_pkl="$out_dir/pickle/wTagCR/$year/h.pkl"

#Link the templates to the working directory
cd templates
mkdir -p $year
cd $year
ln -s $tnp_pkl .

#Return to the main directory
cd ../../

#Make the histograms
singularity exec -B ${PWD}:/srv -B $out_dir --pwd /srv /cvmfs/unpacked.cern.ch/registry.hub.docker.com/coffeateam/coffea-dask:latest python make_hists_tnp.py $year

#Build workspace
conda run -n vhbb --no-capture-output python scalesmear.py -i templates/$year/TnP.root --plot --scale 4 --smear 0.5

#Run the fit
conda run -n combine --no-capture-output python sf.py --fit single -t templates/$year/TnP_var.root -o templates/${year}/${year}_FitSingle --scale 4 --smear 0.5

cd templates/${year}/${year}_FitSingle
conda run -n combine --no-capture-output . build.sh
conda run -n combine --no-capture-output combine -M FitDiagnostics --expectSignal 1 -d model_combined.root --cminDefaultMinimizerStrategy 0 --robustFit=1 --saveShapes --saveWithUncertainties --rMin 0.5 --rMax 1.5

cd ../../../
#Plot results
conda run -n plot --no-capture-output python results.py --dir templates/${year}/${year}_FitSingle --year $year --fit prefit