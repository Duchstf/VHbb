"""Divide the pfnanoindex files into several subfiles"""
import os
import json

#Leaving out '2016APV','2016' to check with Jennet on how to split the data.
for year in ['2017','2018']:
    
    os.system('mkdir -p infiles/{}'.format(year))
    
    #Open the pf nano index for each year
    with open('pfnanoindex_{}.json'.format(year), 'r') as f:
        filelist = json.load(f)
    
    #Print all the MC keys
    print("Datasets for {}: ".format(year))
    print(filelist[year].keys())
    keys_list = list(filelist[year].keys())
    
    #Loop through the datasets and create separate json files
    for i,k in enumerate(keys_list):
        
        #Print number of sub samples
        print("{}: {}" .format(k,len(filelist[year][k])))
        
        filelist_redirector = {}
        
        #Save the output files, remember to mark the data
        data_match = ['JetHT', 'SingleMu']
        out_path = 'infiles/{}/{}_{}.json'.format(year, year, keys_list[i] + 'Data' if any([x in keys_list[i] for x in data_match]) else keys_list[i] )
        print("Ouput path: ", out_path)
        
        for dataset, files in filelist[year][k].items():
            print(dataset)
            filelist_redirector[dataset] = ["root://cmsxrootd.fnal.gov/" + f for f in files]
            
        with open(out_path, 'w') as outfile:
            json.dump(filelist_redirector, outfile)

#! Process 2016 and 2016APV separately