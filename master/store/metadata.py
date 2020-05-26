#!/usr/bin/env python3
"""
 metadata.py - Metadata Store object that holds the information
               mapping files to chunks and manages the metadata.
"""

import os.path
import json
from store.filemap import *
from store.metadata_errors import *
from store.chunkhandler import *
from store.metadata_errors import*


class MetadataStorage:
    """
    Interface for master state
    """
    instance = None
    def __init__(self, logfile_path, checkpoint_path):
        self.logfile_path = logfile_path
        self.checkpoint_path = checkpoint_path
        self.store = FileMap()
        self.chunkhandler = ChunkHandler()
        isInstance = self

    def __del__(self):
        instance = None
        del self

    def retrieve_storage(log = 'logs.json', check = 'checkpoint.json'):
        """
        Call metadata instance. 

        Static singleton function
        source: https://python-3-patterns-idioms-test.readthedocs.io/en/latest/Singleton.html
        """

        exist = bool(MetadataStorage.instance)
        return MetadataStorage(log, check) if not exist else MetadataStorage.instance

    def get_chunk(self, filename, chunk_index = None):
        """
        Return metadata in the format [chunkhandle, size, replicas];
        """
        try:
            return self.store.retrieve(filename, chunk_index)
        except KeyError:
            raise FileNameKeyError(filename)
        except IndexError:
            raise ChunkIndexError(filename, chunk_index)
            
    
    def mutate_chunk(self, filename, chunk_index, size):
        """
        Update store to reflect chunk creations and mutations
        """
        try:
             self.store.update(filename, chunk_index, [size]) 
        except KeyError:
            raise FileNameKeyError(filename)
        except IndexError:
            raise ChunkIndexError(filename, index)

        # logging
        self.write_to_log("mutate_chunk", [filename, chunk_index, size])

    def create_chunk(self, filename, chunkhandle, chunkservers):
        """
        Append a new chunk to file
        """
        try:
            self.store.update(filename, chunk_index, 
                             [chunkhandle, 0], chunkservers)
        except KeyError:
            raise FileNameKeyError(filename)
       
        # logging
        self.write_to_log("create_chunk", [filename, chunkhandle, chunkservers])

    def create_path(self, filename):
        """
        Create file or directory with no chunks if it doesnt exist
        If string ends with `/`, a directory is created
        """

        if not self.store.make_path:
            return "Path already exists"
        
        # logging
        self.write_to_log("create_path", [filename])

    def verify_path(self, filename):
        """
        Verify file or directory exists
        If string ends with `/`, a directory is searched
        """

        return self.store.verify_path(filename)

    def remove(self, filename, chunk_index = None):
        """
        Remove chunkhandle or remove all chunkhandles from file 
        if none are specified
        """
        try:
            self.store.remove(filename, chunk_index)
        except KeyError:
            raise FileNameKeyError(filename)
        except IndexError:
            raise ChunkIndexError(filename, index)
        
        # logging
        self.write_to_log("remove", [filename, chunk_index])

    def toggle(self, chunkserver,on=True):
        """
        Access filemap function of the same name. 

        Add an active server or remove an inactive one. ONLY
        TOGGLES OFF CURRENTLY
        """

        self.store.toggle(chunkserver, on)

        # logging
        self.write_to_log("toggle", [chunkserver, on])

    def locate(self):
        """
        List active chunkservers
        """
        return self.store.list_chunkservers()

    def get_chunk_handle(self):
        return self.chunkhandler.get_chunkservers()

    def recover(self):
        """
        Recovers the master's state on startup
        Uses the latest checkpoint (master.json) if available and then reads logs (logs.json)
        This function needs to be called at master startup
        """

        # Restore the latest checkpoint from checkpoint.json 
        with open(self.checkpoint_path) as json_file:
            checkpoint = json.load(json_file) 
        # update current state   
        self.store.files = checkpoint["files"]
        self.store.chunkhandle_map = checkpoint["chunkhandles"]

        # Plays logs (from logs.json) on top of the current state
        with open(self.logfile_path) as json_file:
            log_file = json.load(json_file)
            
            for log in log_file["logs"]:
                function_name = log["function_name"]
                arguments = log["arguments"]
                # calls a given function with arguments on current class' state
                getattr(self,  function_name)(*arguments)


    def write_to_log(self, function_name, arguments):
        """
        Writes a log to logs.json

        This function is called every time some important operation has 
        been executed. 

        Call example:
        self.write_to_log("function_name", ["arguments", "as", "a", "list", "here"])
        """

        # creates a new log
        new_log = {
            "function_name": function_name,
            "arguments": arguments
        }

        # read
        with open(self.logfile_path) as json_file:
            logs = json.load(json_file)
        # appends to the current list of logs
        logs["logs"].append(new_log)

        # write
        with open(self.logfile_path, 'w') as json_file:
            json.dump(logs, json_file, indent = 2)

        # checks the logs.json size and trigger create_checkpoint if needed
        if len(logs["logs"]) + 1 > 5000: # need to decide on the max size of logs
            self.create_checkpoint()
            # don't forget to reset the logs file
            with open(self.log_path, 'w') as json_file:
                json.dump({ "logs": [] }, json_file, indent = 2)


    def create_checkpoint(self):
        """
        Creates a checkpoint in master.json when logs.json gets 
        bigger than a 
        specific limit we need to set. This function is triggered 
        by write_to_log() above
        """

        with open(self.checkpoint_path, 'w') as json_file:
            json.dump(self.store.checkpoint(), json_file, indent = 2)
