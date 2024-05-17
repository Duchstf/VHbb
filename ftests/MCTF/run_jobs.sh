#!/bin/bash

show_help() {
    cat <<'EOF'
Usage: ./myscript.sh <year>
Options:
    -h      Display this help message

This script runs the f-tests for VH MCTF. This is how the f-tests are run:

1. Link the relevant root files (signalregion.root)
2. Run make_each_ptrho.py to make the workspaces for each polynomial order
3. Run submit.sh to submit the jobs. This will run 500 toys for each polynomial order (0,rho) and (0,rho+1)
4. Run ftest.sh to calculate the F-test statistic for each polynomial order (0,rho) and (0,rho+1)
    Example: ./ftest.sh 0 $rho
5. Start from pT=0,rho=0, if the p-value is less than 5%, take the higher order polynomial as baseline and repeat from step 3.
6. Stop when the higher order polynomials all have p-value > 5%.
EOF
}

# Check for help option
if [[ "$1" == "-h" ]]; then
    show_help
    exit 0
fi

# Check if the directory $1 exists
if [ -d "$1" ]; then
    echo "Directory $1 exists. Do you want to remove it? (y/n)"
    read -r response
    if [ "$response" = "y" ]; then
        rm -rf "$1"
        echo "Directory $1 removed."
    else
        echo "Directory $1 not removed."
        exit 1
    fi
else
    echo "Directory $1 does not exist."
fi

SignalRegionDir="/uscms_data/d3/dhoang/VH_analysis/CMSSW_10_2_13/src/VHbb/combine/combine_PNQCDScan"

#Make log dirs
mkdir -p $1/logs

#Go to the year and link all the necessary files
cd $1
ln -s ../scripts/compare.py .
ln -s ../templates/run_ftest_job.sh .
ln -s $SignalRegionDir/$1/signalregion.root .
cd ..
echo "Finish Linking files!!"

#Then run the make_ptrho.py, which in turns run the make_cards_qcd.py for different polynomial orders
echo "Making the workspaces ..."
./make_ptrho.sh $1

#Now run the f-tests jobs
python submit.py -y $1 --pt=0 --rho=0
python submit.py -y $1 --pt=0 --rho=1
python submit.py -y $1 --pt=0 --rho=2
python submit.py -y $1 --pt=1 --rho=0
python submit.py -y $1 --pt=1 --rho=1
python submit.py -y $1 --pt=1 --rho=2