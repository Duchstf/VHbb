# Create a list of ddb and ddc score
declare -a QCD=("0.05" "0.1" "0.15" "0.2" "0.25" "0.3" "0.35" "0.4" "0.45" "0.5" "0.55" "0.6" "0.65" "0.7" "0.75" "0.8" "0.85" "0.9" "0.95" "1.0")

echo "Running pre-scan script ..."

for thres in "${QCD[@]}"
do
    
    IFS=" " read -r -a arr <<< "${thres}"

    i="${arr[0]}"

    echo "QCD CUT: $i"

    ./run_CombineSingle.sh 2017 $i

done