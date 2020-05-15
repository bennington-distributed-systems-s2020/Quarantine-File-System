#!/usr/bin/env python3
"""
    metadata.py - Metadata Store object that holds th:xe information mapping files to chunks.
    Date: 5/12/2020
"""

import os.path
from filemap import FileMap

class Metadata:
    def __init__(self, logfile):
        self.logfile = logfile
         # WAITING FOR THE LOG OPERATIONS TO BE FLESHED OUT 
        self.store = FileMap()

    def __getitem__(self, filename, chunk_index):
        pass
    
    # Update store to reflect chunk creations and mutations
    def __setitem__(self):
        pass

    def __delitem__(self, ):
        pass

    def create(self, filename, , chunkhandle, chunkservers, lease):
        pass

    def remove(self, filename, chunkhandle):
        pass

    def remove_all(self, filename):
        for

    # Return the state. Use this dictionary on FileMap object to restore state
    def checkpoint(self):
        return 

    def toggle(self, chunkserver,on=True):
        pass

    def locate
        return chunkserver

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

    def write_to_log(self):
        pass
    
    def create_checkpoint(self):
        pass

                
