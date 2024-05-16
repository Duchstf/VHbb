#!/bin/bash

cd $1 #go to the year directory

for pt in {0..1}
do
    for rho in {0..3}
    do
        echo "pt: $pt, rho: $rho"
        
        # Construct the directory name
        thedir="pt${pt}rho${rho}"
        mkdir -p "$thedir"
        cd "$thedir"
        
        # Create JSON file with initial values if it doesn't exist
        rm initial_vals.json
        initial_vals=$(python3 -c "import numpy as np; print((np.full(($pt+1, $rho+1), 1)).tolist())")
        thedict="{\"initial_vals\": $initial_vals}"
        echo $thedict > initial_vals.json

        


    done
done

cd ..