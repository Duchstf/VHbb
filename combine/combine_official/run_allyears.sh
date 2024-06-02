#!/bin/bash

# List of directories to check
years=("2016APV" "2016" "2017" "2018")

# Loop through each directory and check if it exists
for dir in "${years[@]}"; do
  if [ ! -d "$dir" ]; then
    echo "Error: Directory $dir does not exist."
    exit 1
  fi
done

# Check if the "allyears" directory exists and prompt for confirmation before removing it
if [ -d "allyears" ]; then
  read -p "Directory 'allyears' exists. Do you want to remove it? (y/n) " choice
  case "$choice" in 
    y|Y ) rm -rf "allyears"
          echo "Directory 'allyears' has been removed. Recreating it";;
    n|N ) echo "Directory 'allyears' has not been removed.";;
    * ) echo "Invalid choice. Directory 'allyears' has not been removed.";;
  esac
else
  echo "Directory 'allyears' does not exist. Creating it"
fi

mkdir -p allyears/output/testModel

# Linking all the qcd models from the subdirectories to the "allyears" directory
cd allyears/output/
for year in "${years[@]}"; do
    #Link the qcd models
    ln -s ../../$year/output/testModel_$year.pkl .
    ln -s ../../$year/output/testModel_qcdfit_$year.root
done

cd testModel
for year in "${years[@]}"; do
    #Link the datacards
    ln -s ../../../$year/output/testModel_$year/testModel_$year.root .
    ln -s ../../../$year/output/testModel_$year/VBin*$year.txt .
    ln -s ../../../$year/output/testModel_$year/muonCR*$year.txt .
done

#Write the build.sh script
combine_command="combineCards.py \\ \n"

# Loop through each year and add the datacards to the combine command
for year in "${years[@]}"; do
    for file in *$year.txt; do
        filename_without_extension="${file%.txt}"
        combine_command+="$filename_without_extension=$file "
    done

    if [ "$year" != "2018" ]; then
        combine_command+="\\ \n"
    else
        combine_command+="> model_combined.txt \n"
    fi
done

combine_command+="\n"

# Add the text2workspace command
combine_command+="text2workspace.py model_combined.txt -P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel --PO 'map=.*/ZH:rVH[1,-9,10]' --PO verbose --PO 'map=.*/WH:rVH[1,-9,10]' --PO 'map=.*/VV:rVV[1,-9,10]' \n"

# Remove trailing space
combine_command=$(echo -e "$combine_command" | sed 's/[[:space:]]*$//')

echo -e "$combine_command" > build.sh
chmod +x build.sh

#Run the build script
conda run -n combine --no-capture-output ./build.sh > build.out

#After that run the expected shape and significance scripts
cd ../../
ln -s -f ../year_scripts/*.sh .

conda run -n combine --no-capture-output ./exp_shapes.sh $2 > exp_shapes.out 
conda run -n combine --no-capture-output ./exp_significance.sh $2 > significance_VH.txt
conda run -n combine --no-capture-output ./exp_significance_VV.sh $2 > significance_VV.txt 

#Plot
add_all='--cats VBin0fail:VBin0fail*;VBin0pass:VBin0pass*;VBin1fail:VBin1fail*;VBin1pass:VBin1pass*;VBin2fail:VBin2fail*;VBin2pass:VBin2pass*;muonCRfail:muonCRfail*;muonCRpass:muonCRpass*'
if [ "$2" == "unblind" ]; then
    conda run -n plot --no-capture-output combine_postfits -i fitDiagnosticsTest.root $add_all -o plots/test_plot --data --style ../files/style_D.yml --onto qcd --sigs VH --bkgs QCD,qcd,ttbar,singlet,WjetsQQ,Zjets,Zjetsbb,VV,H,WLNu  --rmap 'VH:rVH' --project-signals 3 --xlabel 'Jet 1 $m_{SD}$ [GeV]' -p 
else
    conda run -n plot --no-capture-output combine_postfits -i fitDiagnosticsTest.root $add_all -o plots/test_plot --MC --style ../files/style_D.yml --onto qcd --sigs VH --bkgs QCD,qcd,ttbar,singlet,WjetsQQ,Zjets,Zjetsbb,VV,H,WLNu  --rmap 'VH:rVH' --project-signals 3 --xlabel 'Jet 1 $m_{SD}$ [GeV]' -p 
fi
