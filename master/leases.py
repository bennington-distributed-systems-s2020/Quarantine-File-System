#!/usr/bin/env python3
"""
    leases.py - Handle lease delegation
    Date: 5/13/2020
"""
from datetime import datetime
from utility import get_chunkservers
import requests
from file_management import *


class Lease:
    def __init__(self, chunk_servers = None):
        self.chunk_lease = {}
    
    def grant_lease(self, chunk_handle, chunk_server_addr=None):
        global metadata_handler
        """
        functionality: grant lease to the given chunk_server_addr
        inputs: chunk_handle and chunk_server_addr, 
        return: True if succeeded, False if not.
        """
        try:
            # get all replicas
            replicas_metadata = metadata_handler.store.chunkhandle_map[chunk_handle][1]
            
            # make a copy of replicas
            replicas = replicas_metadata.copy()

            # name a random chunkserver as primary if it's not been assigned

            if chunk_server_addr == None:
                replica_num = len(replicas)
                print("replicas: ", replicas)
                print("length :", replica_num)

                random_int = randint(0, replica_num -1)
                chunk_server_addr = replicas[random_int]
                print("chunk_server addr : ", chunk_server_addr)

            if chunk_server_addr in replicas:
                replicas.remove(chunk_server_addr)
            
            json_chunk_info = {}
            json_chunk_info["chunk_handle"] = chunk_handle
            json_chunk_info["primary"] = chunk_server_addr
            json_chunk_info["replica"] = replicas
            json_chunk_info["timestamp"] = datetime.now().isoformat() + "Z"

            print("enter the lease func")

            if chunk_handle not in self.chunk_lease:
                self.chunk_lease[chunk_handle] = {"primary": chunk_server_addr, "timestamp": json_chunk_info["timestamp"], "replica": replicas}
                # call lease grant on chunk server
                r = requests.post("http://{0}/lease-grant/".format(chunk_server_addr), json = json_chunk_info)

                if r.status_code == 200:
                    
                    # update chunk size
                    metadata_handler.store.chunkhandle_map[chunk_handle][0] = r.json()
                    print("got 200 response")
                    return json_chunk_info
                else:
                    del self.chunk_lease[chunk_handle]
                    return False
            else:
                self.chunk_lease[chunk_handle]["primary"] = chunk_server_addr
                self.chunk_lease[chunk_handle]["timestamp"] = datetime.now()    
            return json_chunk_info
        except Exception as e:
            raise e
            # return False


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
