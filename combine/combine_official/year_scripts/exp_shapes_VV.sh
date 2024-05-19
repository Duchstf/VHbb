# Determine the year from the directory name                                                                                                                                                
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

#-t -1 keeps us from using the data.
combine -M FitDiagnostics -m 90 output/testModel${year}/model_combined.root --setParameters rVV=1,rVH=1 -t -1 --saveShapes --saveWithUncertainties --cminDefaultMinimizerStrategy 0 --robustFit=1 --redefineSignalPOI rVV --freezeParameters rVH
#combine -M MultiDimFit -m 90 output/testModel${year}/model_combined.root --setParameters rVV=1,rVH=1 -t -1 --cminDefaultMinimizerStrategy 0 --robustFit=1