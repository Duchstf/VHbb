year=$1
pt=$2
rho=$3

cd $year
mkdir -p ftests
cd ftests

#Make the directory for baseline and alternative hypothesis
test1=pt${pt}rho${rho}_vs_pt${pt}rho$((${rho}+1))

jobs_dir=/eos/uscms/store/user/dhoang/vh_ftests/DataTF/$year

#Remove the compare directory if it exists
for dir in "$test1"
do
    if [ -d "$dir" ]
    then
        rm -rf "$dir"
    fi

    mkdir "$dir"

    cd "$dir"

    # Copy the necessary files from the jobs
    if [ `ls *GoodnessOfFit*.root | wc -l` -lt 1 ] # if there are no files in the directory
    then
        cp $jobs_dir/*/${dir}*/*GoodnessOfFit*.root .
    fi

    # Check if there are any files matching the pattern *total.root, if such files are found, remove them
    if ls *total.root 1> /dev/null 2>&1; then
        rm *total.root
    fi

    conda run -n combine --no-capture-output hadd higgsCombineToys.baseline.GoodnessOfFit.mH125.total.root higgsCombineToys.baseline.GoodnessOfFit.mH125.*.root
    conda run -n combine --no-capture-output hadd higgsCombineToys.alternative.GoodnessOfFit.mH125.total.root higgsCombineToys.alternative.GoodnessOfFit.mH125.*.root

    tag1=`echo $dir | sed 's/_vs_.*//'`
    tag2=`echo $dir | sed 's/.*_vs_//'`

    echo $tag1
    echo $tag2

    cp ../../$tag1/higgsCombineObserved.GoodnessOfFit.mH125.root baseline_obs.root
    cp ../../$tag2/higgsCombineObserved.GoodnessOfFit.mH125.root alternative_obs.root

    ln -s ../../../scripts/plot_ftests.py .
    conda run -n plot --no-capture-output python plot_ftests.py

    cd ../

done

cd ../../