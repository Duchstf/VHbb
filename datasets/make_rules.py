"""
Make compilation of all datasets to make rules.
"""

import json

with open('datasets_all.txt', 'w') as txt_file:  # Replace 'output_keys.txt' with your desired output file path

    for year in ['2016', '2016APV' ,'2017', '2018']:

        with open(f'nano_list/datasets_{year}.json', 'r') as f: datasets = json.load(f)

        values_year = datasets.values()

        for value_list in values_year:
            for value in value_list:
                txt_file.write(value + '\n')