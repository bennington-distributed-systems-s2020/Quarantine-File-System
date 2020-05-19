#!/usr/bin/env python3
"""
 store.py - Metadata Store object that holds the information
            mapping files to chunks and manages the metadata.
"""

import os.path
from filemap import *
from metadata_errors import *

class Metadata:
    def __init__(self, logfile):
        self.logfile = logfile
         # WAITING FOR THE LOG OPERATIONS TO BE FLESHED OUT 
        self.store = FileMap()

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
            # The `1` index is `size` in `[chunkhandle, size]`
            self.store[filename][chunk_index][1] = size
        except KeyError:
            raise FileNameKeyError(filename)
        except IndexError:
            raise ChunkIndexError(filename, index)

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

    # Return the state. Use this dictionary on FileMap object to restore state
    def checkpoint(self):
        self.store.checkpoint()

    # Access filemap function of the same name. Add an active server or
    # remove an inactive one
    def toggle(self, chunkserver,on=True):
        self.store.toggle(chunkserver, on)

    # List active chunkservers
    def locate
        return self.store.list_chunkservers()

    # TODO: connect with Zak
    # This function restores the state of the Metadata store from the log file
    def recover(self):
        # Restore the state if log file exists
        if os.path.exist(self.logfile):
            with open(self.logfile, "w+") as logfile:
                # Load JSON from each line. THIS IS ASSUMING JSON FOR EACH LOG
                capture = json.loads(i)
                for i in logfile.readlines():
                    if self.store != {}:
                        if "mutate" in capture:
                            pass
                        if "delete" in capture:
                            pass
                        if "create" in capture:
                            pass
                    else:
                        # Restores checkpoint (only should run on first line)
                        self.store = FileMap(capture)
        else:
            return FileMap()

                
