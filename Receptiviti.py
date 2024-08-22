<<<<<<< HEAD
import itertools
import json
import requests
import glob
import pandas as pd
import ntpath
import os


def receptiviti_send(content):
    url = 'https://api.receptiviti.com/v1/framework'
    api_key = 'c53719ecf6494a48a9d1ca37396130cc' #key and secret
    api_secret = 'M0E3R0SBfT+yDfbtwvjhpEePYrKohPNyw8BSnAUNFOeLeAbrupKBhCTy'
    data = json.dumps({
      'request_id': 'req-1',
      'content': content
    })
    resp = requests.post(url, auth=(api_key, api_secret), data=data)
    print(json.dumps(resp.json(), indent=4, sort_keys=True))

def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)

def remove_n(value):
    return ''.join(value.splitlines())

def saveAsJSON(path, filename, data):
    write_file = os.path.join('.',dir,sample_name_cleaned +'.json')
    with open(write_file, "w+") as f:
        json.dump(data_analysed, f)


#read the min 300 word data from the directory
data_dir=glob.glob('C:/Users/fatih/PycharmProjects/Li_scraper/Crunchbase data/result-350/*.csv') 


for file in itertools.islice(data_dir,1,2):
    df_data = pd.read_csv(file)
    data_as_string = df_data.to_string(index=False, header=False)
    final_content = remove_n(data_as_string)
    sample_name = path_leaf(file)
    sample_name_cleaned = sample_name[:-4] #use when saving receptiviti result
    data_analysed = receptiviti_send(final_content)
    #receptiviti result save directory
    dir = "C:/Users/fatih/PycharmProjects/Li_scraper/Crunchbase data/receptiviti_results"
    saveAsJSON(dir,sample_name_cleaned,data_analysed)


    print(sample_name_cleaned)


