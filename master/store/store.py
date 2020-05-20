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
    def __init__(self, checkpoint_path, log_path):
        self.checkpoint_path = checkpoint_path
        self.log_path = log_path
        self.store = FileMap()
        self.chunkhandler = ChunkHandler()

    # Call metadata instance. Static singleton function
    def retrieveStorage(check = 'checkpoint.json', log = 'logs.json'):
        nonexist = MetadataStorage.__instance
        return MetadataStorage(check, log) if nonexist else MetadataStorage.__instance

    # Return metadata in the format [chunkhandle, size, replicas];
    def get_chunk(self, filename, chunk_index):
        try:
            query = self.store[filename][chunk_index]
            query += [self.store.get_chunkservers(query[0])] #Add chunkserver list
            return query
        except KeyError:
            raise FileNameKeyError(filename)
        except IndexError:
            raise ChunkIndexError(filename, index)
            
    
    # Update store to reflect chunk creations and mutations
    def mutate_chunk(self, filename, chunk_index, size):
        try:
            # The `1` index wis `size` in `[chunkhandle, size]`
            self.store[filename][chunk_index][1] = size
        except KeyError:
            raise FileNameKeyError(filename)
        except IndexError:
            raise ChunkIndexError(filename, index)

    # Append a new chunk to file
    def create_chunk(self, filename, chunkhandle, chunkservers):
        try:
            self.store[filename] += [chunkhandle, 0]
            self.store[chunkhandle] = chunkservers
            #TODO Toggle all chunkservers list to `on`
        except KeyError:
            raise FileNameKeyError(filename)

    # Create file with no chunks if it doesnt exist
    # tbh, i kind of want to move this code into create_chunk
    def create_file(self, filename):
        if filename not in store.files:
            store.files += {filename: {}}
        else:
            return "File already exists"

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
    # This function needs to be called on master startup
    def recover(self):
        # Restore the state if log file exists
        if os.path.exist(self.checkpoint_path):
            with open(self.checkpoint_path, "r") as checkpoint_file:
                capture = json.load(checkpoint_file)
                self.store = FileMap(capture)

            with open(self.log_path, "r") as log_file:
                for i in log_file.readlines():
                    if self.store != {}:
                        if "mutate" in capture:
                            pass
                        if "delete" in capture:
                            pass
                        if "create" in capture:
                            pass
        else:
            return FileMap()

    # Writes a log to logs.json
    # This function is called every time some important operation has been executed
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
        print("CREATE_CHECKPOINT")
        # self.store.checkpoint()
