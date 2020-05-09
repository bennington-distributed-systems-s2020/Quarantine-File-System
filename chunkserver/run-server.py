#!/usr/bin/env python3

# - satchel 5/8
# runs gunicorn with json specified config

import json
import subprocess

config_file = 'chunkserver.json'

def run_server():
    with open(config_file, 'r') as cfg:
        config = json.load(cfg)
        workers = config['workers']
        # popen is done with fork so no zombie processes
        subprocess.Popen([
            "gunicorn", "-w", repr(workers), "-b", "0.0.0.0:8000", "gunicorn:app"
            ])
        exit(0)

if __name__ == '__main__':
    run_server()
