#lease_grant.py - implementation of the lease_grant command
#Quang Tran - 5 20 20

import os, datetime, json, logging

with open("config.json") as config_json:
    config = json.load(config_json)

def lease_grant(chunk_handle: str, timestamp: str, replica: list) -> int:
    """
    Grant a lease to a chunk.

    chunk_handle: str: The chunkhandle of the respective chunk.
    timestamp: str: The timestamp of the lease.
    replica: list: A list containing the locations of the replica of the primary chunk.

    return: int: The size of the chunk being given the lease.
    """
