#lease_grant.py - implementation of the lease_grant command
#Quang Tran - 5 20 20

import os, datetime, json, logging
import dateutil.parser

with open("config.json") as config_json:
    config = json.load(config_json)

#replicas interaction is dependent on how append is implemented
#so i will hold off on that
def lease_grant(chunk_handle: str, timestamp: str, replica: list) -> int:
    """
    Grant a lease to a chunk.

    chunk_handle: str: The chunkhandle of the respective chunk.
    timestamp: str: The timestamp of the lease.
    replica: list: A list containing the locations of the replica of the primary chunk.

    return: int: The size of the chunk being given the lease.
    """
    with open(config["CHUNK_PATH"] + chunk_handle + '.chunk', 'rb+') as f:
        f.seek(1)
        f.write(b'\x01') #update to notify that the chunk has a lease

        lease_timestamp_obj = dateutil.parser.parse(timestamp)
        f.seek(2)
        f.write(lease_timestamp_obj.year.to_bytes(2, 'big')) #write year
        f.write(lease_timestamp_obj.month.to_bytes(1, 'big')) #write month
        f.write(lease_timestamp_obj.day.to_bytes(1, 'big')) #write day
        f.write(lease_timestamp_obj.hour.to_bytes(1, 'big')) #write day
        f.write(lease_timestamp_obj.minute.to_bytes(1, 'big')) #write day
        f.write(lease_timestamp_obj.second.to_bytes(1, 'big')) #write day

    return os.path.getsize(config["CHUNK_PATH"] + chunk_handle + '.chunk') - 9 #9 starting bytes
