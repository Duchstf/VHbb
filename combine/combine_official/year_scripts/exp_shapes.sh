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
elif [[ "$PWD" == *"allyears"* ]]; then
    year=""
fi

if [[ "$1" == "unblind_sideband" ]]; then
combine -M FitDiagnostics -m 125 output/testModel${year}/model_combined.root --setParameters rVH=1,rVV=1 --freezeParameters rVH,rVV --saveShapes --saveWithUncertainties --cminDefaultMinimizerStrategy 0 --robustFit=1

elif [[ "$1" == "unblind" ]]; then
combine -M FitDiagnostics -m 125 output/testModel${year}/model_combined.root --setParameters rVH=1,rVV=1 --saveShapes --saveWithUncertainties --cminDefaultMinimizerStrategy 0 --robustFit=1

else
#-t -1 keeps us from using the data.
combine -M FitDiagnostics -m 125 output/testModel${year}/model_combined.root --setParameters rVH=1,rVV=1 --saveShapes --saveWithUncertainties --cminDefaultMinimizerStrategy 0 --robustFit=1 -t -1
fi

