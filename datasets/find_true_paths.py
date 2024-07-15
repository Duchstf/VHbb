"""
Use xrdfs root://cmseos.fnal.gov ls -u /store/ to find the true paths of the files
"""

import os
import json
import subprocess, sys

file_path = 'infiles/2018/2018_VBFHToBB_DipoleRecoilOn.json'

# Function to update URLs in the JSON data
def update_urls(data):
    updated_data = {}
    for key, urls in data.items():
        updated_urls = []
        for url in urls:
            base_path = url.split('//')[2]  # Extract the base path
            # Use xrdfs to find the true path
            command = f"xrdfs root://cmseos.fnal.gov ls -u /{base_path}"
            true_path = subprocess.getoutput(command).split('\n')[0]
            updated_urls.append(true_path)
        updated_data[key] = updated_urls
    return updated_data


input_file = file_path
output_file = file_path

with open(input_file, 'r') as file: data = json.load(file)

# Update the URLs
updated_data = update_urls(data)

# Write the updated JSON data back to a file
with open(output_file, 'w') as file: json.dump(updated_data, file, indent=4)

print(f"URLs updated successfully and saved to {output_file}")