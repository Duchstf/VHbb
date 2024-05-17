year=$1
pt=$2
rho=$3

cd $year
mkdir -p ftests
cd ftests

#Make the directory for baseline and alternative hypothesis
tag=pt${pt}rho${rho}_vs_pt${pt}rho$((${rho}+1))
jobs_dir=/eos/uscms/store/user/dhoang/vh_ftests/MCTF/$year

#Remove the compare directory if it exists
if [ -d $tag ]
then
    rm -rf $tag
fi

#Make the compare directory
mkdir $tag
cd $tag

# Copy the necessary files from the jobs
if [ `ls *GoodnessOfFit*.root | wc -l` -lt 1 ] # if there are no files in the directory
then
    cp $jobs_dir/*/${tag}*/*GoodnessOfFit*.root .
fi

# Check if there are any files matching the pattern *total.root
if ls *total.root 1> /dev/null 2>&1; then
    # If such files are found, remove them
    rm *total.root
fi

conda run -n combine --no-capture-output hadd higgsCombineToys.baseline.GoodnessOfFit.mH125.total.root higgsCombineToys.baseline.GoodnessOfFit.mH125.*.root
conda run -n combine --no-capture-output hadd higgsCombineToys.alternative.GoodnessOfFit.mH125.total.root higgsCombineToys.alternative.GoodnessOfFit.mH125.*.root

tag1=`echo $tag | sed 's/_vs_.*//'`
tag2=`echo $tag | sed 's/.*_vs_//'`

echo $tag1
echo $tag2

pwd
cp ../../$tag1/higgsCombineObserved.GoodnessOfFit.mH125.root baseline_obs.root
cp ../../$tag2/higgsCombineObserved.GoodnessOfFit.mH125.root alternative_obs.root

ln -s ../../../scripts/plot_ftests.py .
conda run -n combine --no-capture-output python plot_ftests.py

#Go back to OG directory
cd ../../../