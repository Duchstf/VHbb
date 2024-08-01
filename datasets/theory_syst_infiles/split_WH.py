import json, sys

year = sys.argv[1]
WH_filepath = f'../infiles/{year}/{year}_WH.json'

with open(WH_filepath, 'r') as file: WH_dict = json.load(file)
print(list(WH_dict.keys()))

for key, value in WH_dict.items():

    filename=f'{year}/{year}_{key}.json'
    with open(filename, 'w') as json_file: json.dump({key:value}, json_file)