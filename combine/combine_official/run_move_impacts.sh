mkdir -p impact_plots

#Move impacts.pdf from each year to this directory

# List of directories to check
years=("2016APV" "2016" "2017" "2018")

# Loop through each directory and check if it exists
for dir in "${years[@]}"; do
  if [ ! -d "$dir" ]; then
    echo "Error: Directory $dir does not exist."
    exit 1
  else
    cp $dir/impacts.pdf impact_plots/$dir.pdf
  fi
done

 cp allyears/impacts.pdf impact_plots/allyears.pdf