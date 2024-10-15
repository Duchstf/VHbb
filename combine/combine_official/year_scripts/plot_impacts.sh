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

#Run impacts_fit first
#Add -spool to condor submit command, like this: condor_submit -spool condor_run_impacts.sub
#Then run these interactively
modelfile=output/testModel${year}/model_combined.root

combineTool.py -M Impacts -d $modelfile -m 125 -o impacts.json --exclude 'rgx{qcdparams*}' --redefineSignalPOIs rVH --blind
plotImpacts.py -i impacts.json -o impacts
