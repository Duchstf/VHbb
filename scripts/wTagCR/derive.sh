#This script is used to derive the wTag CR templates from the data
pkl_dir = 
year = $1

#Link the templates to the working directory
mkdir -p templates

cd templates
mkdir -p $year
cd $year
ln -s 