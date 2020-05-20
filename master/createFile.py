"""
file_name: createFile.py

functionality: Used for creating a new file for a client.
1. it assignes the new file

Date: May 17th, 2020
Author: Zhihong Li
"""

import os
import json
from store import store

chunk_handle_counter_json = "chunkHandlerCounter.json"
logfile_path = "logs.json"
checkpoint_path = "checkpoint.json"

metadata_handler = store.MetadataStorage(logfile_path, checkpoint_path)

def create_new_file(file_name, directory_path, file_size, meatadata_handler):
    if file_name is None or type(file_name) != str:
        return False # could also pass error message with a tuple: (False, "file_name is empty")
    
    # verify the path
    if directory_path is None or type(file_name) != str or meatadata_handler.verify_path(directory_path):
        return False
    
    # verify filesize
    if file_size is None or (file_size < 0) or type(file_size) != int:
        return False
    global chunk_handle_counter_json
    number_of_chunks_needed = get_chunk_size_needed(file_size)
    chunk_handle_list = get_chunk_handle(number_of_chunks_needed)

    # create new file with number of chunks in the metadata

def create_new_directory(directoryName, directory_path):
    global metadata_handler
    
    # make sure the path is valid, traverse the path to the valid directory

    # if valid, add the new directory in the metadata
    
    # log the operation

def remove_file(file_path):
    global metadata_handler
    # if fila_path valid:
        # remove the file
    # else:
        # return error code // file does not exist
    # end

# this is the function that you use to get chunkHandle according to number of chunks needed
def get_chunk_handle(number_of_chunks_needed):
    global metadata_handler    
    handleList = create_chunk_handle(number_of_chunks_needed)
    return handleList    

def create_chunk_handle(number_of_chunks_needed):
    global metadata_handler
    global chunk_handle_counter_json
    handleList = []
    for i in range(number_of_chunks_needed):
        newHandle = metadata_handler.get_chunk_handle()
        handleList.append(newHandle)
    return handleList


# file size is in byte
def get_chunk_size_needed(file_size):
    one_mb = 1000000 # 1mb = 1000000 bytes
    chunk_size_offset = 16 
    one_chunk_size_in_byte = one_mb * 64 - chunk_size_offset

    if file_size % one_chunk_size_in_byte == 0:
        number_of_chunks_needed = file_size / one_chunk_size_in_byte
        return number_of_chunks_needed
    else:
        number_of_chunks_needed = int(file_size / one_chunk_size_in_byte) + 1
        return number_of_chunks_needed

if __name__ == "__main__":
    # testing
    r = get_chunk_handle(20)
    print(r)

    
    """
    getchunk- returns a list [chunkhandle, size, [replicas]]

    Inputs: 
    file name
    folder Path (namespace)
    file_size(unit MB)

    What happens in the function:
    Get number of chunks needed for the file
    create file metadata (namespace, chunks with handles)
    Assign three chunkservers to own the file. (chunkservers that holds the file namespace and chunks)
    Create metadata for the new file (includes file namespace:chunks(with index) and handles, chunkservers
    that holds it)
    Append new metadata and namespace to the namespace-metadata map file
    Assign a primary for all the chunks and return it and all other replicas locations. (maybe chunkservers 
    that holds the chunks) because the client will ask the chunkserver for access and write or read. If 
    chunkserver is not primary, they will ask us for it. (might be some special cases here)

    """