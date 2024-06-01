# Arguments
year=""


if [[ "$PWD" == *"2016APV"* ]]; then
    year="_2016APV"
elif [[ "$PWD" == *"2016"* ]]; then
    year="_2016"
elif [[ "$PWD" == *"2017"* ]]; then
    year="_2017"
elif [[ "$PWD" == *"2018"* ]]; then
    year="_2018"
fi

#Clean up 
rm condor_run_impacts*
rm higgsCombine_*Fit_Test*

modelfile=output/testModel${year}/model_combined.root
taskname="run_impacts"

# Do initial fit
combineTool.py -M Impacts -d $modelfile -m 125 --doInitialFit --setParameters rVH=1 --robustFit 1 --toysFr -t -1

# Do more fits
combineTool.py -M Impacts -d $modelfile -m 125 --doFits --setParameters rVH=1 --robustFit 1 --job-mode condor --exclude 'rgx{qcdparams*}' --sub-opts='+JobFlavour = "workday"' --task-name $taskname --toysFr -t -1

#Then add -spool to condor_submit
#Then run plot_impacs.sh