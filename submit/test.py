import os, sys
import subprocess

# Add path so the script sees the modules in parent directory
sys.path.append('/srv')

year = sys.argv[1]
tag = "vhbb_theory_systematics"
CR_list = ['WH', 'ttH', 'ggF', 'VBFHToBBDipoleRecoilOn', 'VV', 'ZHHToBBZToQQ', 'ZHHToBBZToLL', 'ZHHToBBZToNuNu', 'ggZHHToBBZToQQ', 'ggZHHToBBZToLL', 'ggZHHToBBZToNuNu']
out_path = "output/coffea/{}/{}/".format(tag,year)

#Input PF nano for the year
infiles = subprocess.getoutput("ls datasets/theory_syst_infiles/{}/{}_*.json".format(year, year)).split()

for this_file in infiles:
    index = ''.join(this_file.split("_")[3:]).split(".json")[0]
    outfile = out_path + '{}_dask_{}.coffea'.format(year, index)
    
    if index not in CR_list:
        print("{} is in ingore list, skipping ...".format(index))
        continue

    if os.path.isfile(outfile):
        print("File " + outfile + " already exists. Skipping.")
        continue 

    else:
        print("Begin running " + outfile)