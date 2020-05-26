#!/usr/bin/env python3
"""
    leases.py - Handle lease delegation
    Date: 5/13/2020
"""
from datetime import datetime
from utility import get_chunkservers
import requests

class Lease:
    def __init__(self, chunk_servers = None):
        self.chunk_lease = {}
    
    def grant_lease(self, chunk_handle, chunk_server_addr):
        """
        functionality: grant lease to the given chunk_server_addr
        inputs: chunk_handle and chunk_server_addr, 
        return: True if succeeded, False if not.
        """
        try:
            if chunk_handle not in self.chunk_lease:
                self.chunk_lease[chunk_handle] = {"primary": chunk_server_addr, "timestamp": datetime.now()}
            else:
                self.chunk_lease[chunk_handle]["primary"] = chunk_server_addr
                self.chunk_lease[chunk_handle]["timestamp"] = datetime.now()    
            return True
        except:
            return False


    def provoke_lease(self, chunk_handle):
        """
        functionality: Revokes a lease from the primary chunkserver attached to a lease.
        parameter: chunk_handle
        return True when succeeded
        """
        try:
            if chunk_handle in self.chunk_lease:
                self.chunk_lease[chunk_handle]["primary"] = None
                self.chunk_lease[chunk_handle]["timestamp"] = None
            return True
        except:
            return False
        return True
lease = Lease()

if __name__ == "__main__":
    lease = Lease()
    lease.grant_lease("102992a28c", "http://127.0.0.1:8000")
    print(lease.chunk_lease)
    lease.provoke_lease("102992a28c")
    print(lease.chunk_lease)
