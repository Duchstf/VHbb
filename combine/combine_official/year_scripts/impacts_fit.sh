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
combineTool.py -M Impacts -d $modelfile -m 125 --doInitialFit --robustFit 1 --redefineSignalPOIs rVH --setParameters rVV=1,rVH=1

# Do more fits
combineTool.py -M Impacts -d $modelfile -m 125 --doFits --robustFit 1 --redefineSignalPOIs rVH --setParameters rVV=1,rVH=1 --job-mode condor --exclude 'rgx{qcdparams*}' --sub-opts='+JobFlavour = "workday"' --task-name $taskname 

#Then add -spool to condor_submit
#Then run plot_impacts.sh
