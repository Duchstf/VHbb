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

echo "VH SIGNIFICANCE"
if [ "$1" == "unblind" ]; then
combine -M Significance -m 125 --signif output/testModel${year}/model_combined.root --cminDefaultMinimizerStrategy 0 --redefineSignalPOI rVH --setParameters rVH=1 --verbose 9
else
combine -M Significance -m 125 --signif output/testModel${year}/model_combined.root --cminDefaultMinimizerStrategy 0 --redefineSignalPOI rVH --setParameters rVH=1 --verbose 9 -t -1
fi