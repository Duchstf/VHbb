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
# rm condor_run_impacts*
# rm higgsCombine_*Fit_Test*

modelfile=output/testModel${year}/model_combined.root

for bias in 0 1 `seq 5 5 10`
    do
    combineTool.py -M FitDiagnostics  -t -1 --redefineSignalPOIs rVH --expectSignal $bias -n bias$bias -d $modelfile --cminDefaultMinimizerStrategy 0 --robustFit=1 -t 20 -s 1:50:1 --job-mode condor --sub-opts='+JobFlavour = "workday"' --task-name VH$bias
    done

# for bias in 0 1 `seq 5 5 100`
#     do 
#     hadd -f bias$bias.root *Combinebias$bias.*
#     done