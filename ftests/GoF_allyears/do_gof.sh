#!/bin/bash
ALGO=saturated
echo "Using algo:" $ALGO

#Copy model combine over
allyears_model="../../combine/combine_official/allyears/output/testModel/model_combined.root"

if [[ "$1" -eq 0 ]]; then
    combine -M FitDiagnostics -d $allyears_model  --setParameters rVV=1,rVH=1 -n "" --cminDefaultMinimizerStrategy 0 --robustFit=1 --saveShapes --saveWithUncertainties 
elif [[ "$1" -eq 1 ]]; then
    combine -M GoodnessOfFit -d $allyears_model --algo $ALGO -n DataGoF$ALGO
elif [[ "$1" -eq 2 ]]; then
    rm higgsCombineGoFs$ALGO.GoodnessOfFit.mH120.*.root
    combineTool.py -M GoodnessOfFit $allyears_model --algo $ALGO -t 30 --toysFrequentist -n GoFs$ALGO --job-mode condor --sub-opts='+JobFlavour = "workday"' --task-name VH$ALGO -s 1:100:1    
elif [[ "$1" -eq 3 ]]; then 
    hadd -f allgofs$ALGO.root higgsCombineGoFs$ALGO.GoodnessOfFit.mH120.*.root
elif [[ "$1" -eq 4 ]]; then 
    python plot_single_gof.py higgsCombineDataGoF$ALGO.GoodnessOfFit.mH120.root allgofs$ALGO.root --algo $ALGO --year "$3"
fi
