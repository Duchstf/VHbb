year=""

if [[ "$PWD" == *"2016"* ]]; then
    year="_2016"
elif [[ "$PWD" == *"2017"* ]]; then
    year="_2017"
elif [[ "$PWD" == *"2018"* ]]; then
    year="_2018"
fi

combineTool.py -M Impacts -d output/testModel${year}/model_combined.root --setParameters rVV=1 -t -1 --doInitialFit --robustFit=1 
combineTool.py -M Impacts -d output/testModel${year}/model_combined.root -m 90 --robustFit 1 --doFits
combineTool.py -M Impacts -d output/testModel${year}/model_combined.root -m 90 -o impacts.json