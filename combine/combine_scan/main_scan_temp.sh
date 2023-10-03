#!/bin/bash

# Create a list of ddb and ddc score
declare -a pairs=(THRES_LIST)

eval `scramv1 runtime -sh`

for thres in "${pairs[@]}"
do
    IFS=" " read -r -a arr <<< "${thres}"

    i="${arr[0]}"
    j="${arr[1]}"

    echo "DDB: $i; DDC: $j"

    cd DDB-$i-DDC-$j/2017

    cd ..

    cp ../make_cards.py .

    python make_cards.py 2017

    #Run combine
    cd 2017
    ln -sf ../../make_workspace.sh .
    ln -sf ../../exp_significance.sh .

    pwd
    ls 

    source make_workspace.sh

    echo "DDB: $i; DDC: $j >>>"
    source exp_significance.sh
    echo ">>>>>>>>>>>>>>>>"

    cd ../../

    pwd
done
