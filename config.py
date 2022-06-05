
from typing import Dict, List
import json
import sys
import os

dir_path = os.path.dirname(os.path.realpath(__file__))

def read_source_dirs() -> List[str]:
    dirs: List[str] = []
    for line in sys.stdin:
        line = line.strip()
        if not line:
            return dirs
        path = os.path.abspath(os.path.expanduser(line))
        if os.path.exists(path):
            dirs.append(path)
        else:
            print(f'{path} is not a directory.')

def read_target_dir() -> str:
    path = ""
    while True:
        path = os.path.abspath(os.path.expanduser(input().strip()))
        if not os.path.exists(path):
            print(f"path '{path}' does not exist.")
        else:
            return path

def read_yes_or_no(question: str) -> bool:
    ans = ''
    while not ans in ['yes','no']:
        print(question)
        ans = input().strip()
        if not ans in ['yes', 'no']:
            print("please type 'yes' or 'no'")
    
    return ans == 'yes'

    
def init_config() -> {}:
    config_filename = os.path.join(dir_path, 'config.json')

    if os.path.exists(config_filename):
        with open(config_filename, 'r') as fin:
            config = json.load(fin)
        return config
    
    config = {
        'extensions' : ['.jpg', '.jpeg', '.JPG', '.JPEG']
    }

    print("no config has been set yet, so let's start.")
    
    config['source_dirs'] = []
    while not config['source_dirs']:
        print("from which directories do you want to import pictures (blank line finishes input)?")
        config['source_dirs'] = read_source_dirs()

    config['target_dir'] = ""
    while not config['target_dir']:
        print("where do you want your images to be stored?")
        config['target_dir'] = read_target_dir()

    config['keep_filename'] = read_yes_or_no("do you want to keep the filename?")
    config['prepend_timestamp'] = read_yes_or_no("do you want to prepend the timestamp?")
    config['copy'] = read_yes_or_no("copy files instead of moving?")

    if read_yes_or_no("store config?"):
        with open(config_filename, 'w') as fout:
            fout.write(json.dumps(config, indent=4))

    return config
