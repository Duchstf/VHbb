#!/bin/bash

cd $1 #go to the year directory

pt=0
for rho in {0..0}
do
    echo "pt: $pt, rho: $rho"
    
    # Construct the directory name
    thedir="pt${pt}rho${rho}"
    mkdir -p "$thedir"
    cd "$thedir"
    
    # Create JSON file with initial values if it doesn't exist
    [ -f initial_vals.json ] && rm initial_vals.json
    initial_vals=$(python3 -c "import numpy as np; print((np.full(($pt+1, $rho+1), 1)).tolist())")
    thedict="{\"initial_vals\": $initial_vals}"
    echo $thedict > initial_vals.json

    # Create the workspace
    [ -f make_cards_qcd.py ] && rm make_cards_qcd.py
    ln -s ../../scripts/make_cards_qcd.py .
    conda run -n combine --no-capture-output python make_cards_qcd.py > out_make_cards.txt
    
    # Build the workspace
    cd output/testModel_$1
    chmod +rwx build.sh
    conda run -n combine --no-capture-output ./build.sh
    cd ../..
    
    #Run combine tools
    conda run -n combine --no-capture-output combine -M MultiDimFit -m 125 -d output/testModel_$1/model_combined.root --saveWorkspace --setParameters r=0 --freezeParameters r -n Snapshot --robustFit=1 --cminDefaultMinimizerStrategy 0 > multiDimFit.txt
    conda run -n combine --no-capture-output combine -M GoodnessOfFit -m 125 -d higgsCombineSnapshot.MultiDimFit.mH125.root --snapshotName MultiDimFit --bypassFrequentistFit --setParameters r=0 --freezeParameters r -n Observed --algo saturated --cminDefaultMinimizerStrategy 0 > goodnessOfFit.txt

    #Go back
    cd ..

done

cd ..