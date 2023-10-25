#!/bin/bash

#! WARNING: you eed to create the year's directory and include the pickle file first!
#EXAMPLE: ./run_CombineSingle.sh 2016

#Make the histograms
singularity exec -B ${PWD}:/srv --pwd /srv /cvmfs/unpacked.cern.ch/registry.hub.docker.com/coffeateam/coffea-dask:latest python make_hists.py $1

#Activate the environment
cmsenv

#Produce combine cards
python make_cards.py $1

#Run the combine jobs
cd $1

mkdir -p plots

ln -s -f ../year_scripts/*.C .
( GLOBIGNORE="*_VV.sh"; ln -s -f ../year_scripts/*.sh . )

./make_workspace.sh
./exp_shapes.sh 

#Produce the relevant plots
root -b -q draw_MC.C
root -b -q draw_DataFit.C
#root -b draw_PFratio_QCDMC.C

./exp_significance.sh

cd ../