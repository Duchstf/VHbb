import json, sys

year = sys.argv[1]
ZH_filepath = f'../infiles/{year}/{year}_ZH.json'

with open(ZH_filepath, 'r') as file: ZH_dict = json.load(file)
print(list(ZH_dict.keys()))

for key, value in ZH_dict.items():

    filename=f'{year}/{year}_{key}.json'
    with open(filename, 'w') as json_file: json.dump({key:value}, json_file)