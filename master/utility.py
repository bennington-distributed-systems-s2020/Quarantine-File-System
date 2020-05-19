#!/usr/bin/env python3
"""
    utility.py -- general helper functions
    Date: 5/13/2020
"""
import json

chunkservers = None
def get_chunkservers():
    """
    Returns all chunkserver IPs as listed in the JSON configuration. 
    Only reads from disk once, caches result.
    """
    if chunkservers != None:
        return chunkservers
    config_file = 'master.json'
    with open(config_file, 'r') as cfg:
        config = json.load(cfg)
        chunkservers = config['chunkservers']
        formatted = [
            "http://" + ip + ":" + repr(port) 
            for (ip, port) in chunkservers
            ]
        chunkservers = formatted
        return chunkservers