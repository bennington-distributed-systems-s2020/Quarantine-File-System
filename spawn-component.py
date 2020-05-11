#!/usr/bin/env python3

# - satchel 5/8
# runs gunicorn with json specified config

import json
import subprocess
import sys

config_master = "./config/master.json"
config_chunk = "./config/chunkserver.json"

def spawn_component():
    component = sys.argv[1]
    config_file = ""
    if component == "master":
        config_file = "./config/master.json"
    if component == "master":
        config_file = "./config/master.json"
    with open(config_file, 'r') as cfg:
            
        config = json.load(cfg)
        workers = config['workers']
        # popen is done with fork so no zombie processes
        subprocess.Popen([
            "gunicorn", "-w", repr(workers), "-b", "0.0.0.0:8000", "gunicorn:app"
            ])
        exit(0)

if __name__ == '__main__':
    spawn_component()
