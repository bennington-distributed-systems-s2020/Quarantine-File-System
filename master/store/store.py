#!/usr/bin/env python3
"""
 store.py - Metadata Store object that holds the information
            mapping files to chunks and manages the metadata.
"""

import os.path
import json
from filemap import *
from metadata_errors import *
from chunkhandler import *

# Interface for master state
class MetadataStorage:
    def __init__(self, logfile_path, checkpoint_path):
        self.logfile_path = logfile_path
        self.checkpoint_path = checkpoint_path
        self.store = FileMap()
        self.chunkhandler = ChunkHandler()

    # Call metadata instance. Static singleton function
    def retrieveStorage(check = 'checkpoint.json', log = 'logs.json'):
        nonexist = MetadataStorage.__instance
        return MetadataStorage(check, log) if nonexist else MetadataStorage.__instance

    # Return metadata in the format [chunkhandle, size, replicas];
    def get_chunk(self, filename, chunk_index):
        try:
            return self.store.retrieve(filename, chunk_index)
        except KeyError:
            raise FileNameKeyError(filename)
        except IndexError:
            raise ChunkIndexError(filename, index)
            
    
    # Update store to reflect chunk creations and mutations
    def mutate_chunk(self, filename, chunk_index, size):
        try:
            # The `1` index wis `size` in `[chunkhandle, size]`
            self.store.update(filename, chunk_index, [0])
        except KeyError:
            raise FileNameKeyError(filename)
        except IndexError:
            raise ChunkIndexError(filename, index)

    # Append a new chunk to file
    def create_chunk(self, filename, chunkhandle, chunkservers):
        try:
            self.store.update(filename, chunk_index, [chunkhandle, 0], chunkservers)
            #TODO Toggle all chunkservers list to `on`
        except KeyError:
            raise FileNameKeyError(filename)

    # Create file or directory with no chunks if it doesnt exist
    # If string ends with `/`, a directory is created
    def create_path(self, filename):
        if not self.store.make_path:
            return "Path already exists"

    # Verify file or directory exists
    # If string ends with `/`, a directory is created
    def verify_path(self, filename):
        return self.store.verify_path()

    # Remove chunkhandle or remove all chunkhandles from file if none are specified
    def remove(self, filename, chunk_index = None):
        # coulda done `if not chunkhandle:` but i feel like that's dirty
        if chunkhandle == None:
            del self.store[filename]
        else:
            del self.store[filename][chunkhandle]

    # Access filemap function of the same name. Add an active server or
    # remove an inactive one
    def toggle(self, chunkserver,on=True):
        self.store.toggle(chunkserver, on)

    # List active chunkservers
    def locate():
        return self.store.list_chunkservers()

    #TODO Implement count in checkpoint
    def get_chunk_handle(self):
        self.chunkhandler.get_chunk_handle()

    # Recovers the master's state on startup
    # Uses the latest checkpoint (master.json) if available and then reads logs (logs.json)
    # This function needs to be called at master startup
    def recover(self):
        # Restore the latest checkpoint from checkpoint.json 
        with open(self.checkpoint_path) as json_file:
            checkpoint = json.load(json_file) 
        # update current state   
        self.store.files = checkpoint["files"]
        self.store.chunkhandle_map = checkpoint["chunkhandles"]
        self.chunkhandler.chunkHandleCounter = checkpoint["count"]

        # Plays logs (from logs.json) on top of the current state
        with open(self.logfile_path) as json_file:
            logs = json.load(json_file)
            
            for log in logs:
                # need to decide on action types and parameters


    # Writes a log to logs.json
    # This function is called every time some important operation has been executed
    # Call example:
    # self.write_to_log("DELETE", {"filename": "test.txt", "chunk_index": 3})
    def write_to_log(self, action_type, details):
        # creates a new log
        new_log = {
            "action_type": action_type,
            "details": details
        }

        # read
        with open(self.log_path) as json_file:
            logs = json.load(json_file)

        # appends to the current list of logs
        logs["logs"].append(new_log)

        # write
        with open(self.log_path, 'w') as json_file:
            json.dump(logs, json_file, indent = 2)

        # checks the logs.json size and trigger create_checkpoint if needed
        if len(logs["logs"]) + 1 > 5000: # need to decide on the max size of logs
            self.create_checkpoint()


    # Creates a checkpoint in master.json when logs.json gets bigger than a specific limit we need to set
    # This function is triggered by write_to_log() above
    def create_checkpoint(self):
        with open(self.checkpoint_path, 'w') as json_file:
            json.dump(self.store.checkpoint() + {"count": self.chunkhandler.chunkHandleCounter}, json_file, indent = 2)