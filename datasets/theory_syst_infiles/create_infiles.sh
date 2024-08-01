#!/bin/bash

# Define the years in an array
years=("2016" "2016APV" "2017" "2018")
samples=("ttH" "WH" "ggF" "VV" "VBFHToBB_DipoleRecoilOn")

# Loop through each year in the array
for year in "${years[@]}"
do
  echo "Processing year: $year"
  # Clear everything in the directory
  rm -rf $year

  # Create the directory
  mkdir $year

  #copy files over
  for sample in "${samples[@]}"
  do
    cp ../infiles/$year/${year}_${sample}.json $year/
  done

  #Split ZH, WH
  python split_ZH.py $year
  python split_WH.py $year

done
