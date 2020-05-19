#!/usr/bin/env python3
"""
    leases.py - Handle lease delegation
    Date: 5/13/2020
"""

from utility import get_chunkservers
import requests

class Lease:
    def __init__(chunk_hex, timestamp, replicas):
        self.chunk_hex = chunk_hex
        self.timestamp = timestamp
        self.replicas  = replicas

def get_all_for_lease(chunk_hex):
    """
    Get all chunkservers that are associated to a given chunk.
    Returns all of them, regardless of if they're primaries or replicas.
    """
    chunkservers = get_chunkservers()
    chunks = []
    for ip in chunkservers:
        r = requests.post(ip + "/lease", data={"chunk": chunk_hex})
        leases.append((ip, r))
    return chunks

def get_primary_for_lease(chunk_hex):   
    """
    Return the primary chunkserver for a given chunk.
    """
    chunks = get_all_for_lease(chunk_hex)
    primary = [
        elem for elem in filter(
            lambda response: response[1]["primary"] == True,
            chunks
            )
        ][0]
    return primary
    
def lease_request_handler(chunk_hex, timestamp, replicas):
    """
    Handler function for the HTTP endpoint for chunkservers to request a lease.
    """
    pass

def lease_grant(chunk_hex, timestamp, replicas):
    """
    Creates a lease and sends it to a chunkserver, granting it.
    """
    lease = Lease(chunk_hex, timestamp, replicas)

def lease_revoke(chunk_hex):
    """
    Revokes a lease from the primary chunkserver attached to a lease.
    """
    pass