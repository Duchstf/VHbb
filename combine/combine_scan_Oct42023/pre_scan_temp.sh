#!/bin/bash

# Create a list of ddb and ddc score
declare -a pairs=(THRES_LIST)

echo "Running pre-scan script ..."

for thres in "${pairs[@]}"
do
    IFS=" " read -r -a arr <<< "${thres}"

    i="${arr[0]}"
    j="${arr[1]}"

    echo "DDB: $i; DDC: $j"
   
    #Make the workspace directory
    mkdir -p DDB-$i-DDC-$j/2017/

    #Copy all the stuff needed over
    cd DDB-$i-DDC-$j/2017/
    ln -sf ../../ParticleNet_msd.pkl .
    cd ../../

    cp make_hists.py DDB-$i-DDC-$j/

    cd DDB-$i-DDC-$j/

    cp ../*.json .

    #Replace the threshold in make_hist
    sed -i "s/ddbthr =.*/ddbthr = $i/g" make_hists.py
    sed -i "s/ddcthr =.*/ddcthr = $j/g" make_hists.py

    #Run make-hist
    python make_hists.py 2017

    cd ../

done

