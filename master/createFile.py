"""
file_name: createFile.py

functionality: Used for creating a new file for a client.
1. it assignes the new file

Date: May 17th, 2020
Author: Zhihong Li
"""
import json
from chunkhandler import ChunkHandler
import os

def create_new_file(file_name, directory_path, file_size, number_of_replicas, chunk_handle_counter_json):
    if file_name is None:
        return False # could also pass error message with a tuple: (False, "file_name is empty")
    # verify the path
    if directory_path is None:
        return False
    # verify the 
    if file_size is None or (file_size < 0) or type(file_size) != type(64):
        return False
    number_of_chunks_needed = get_chunk_size_needed(file_size)
    chunk_handle_list = get_chunk_handle(number_of_chunks_needed, chunk_handle_counter_json)
    get_directory_path_list(directory_path)
    new_file_metadata = {}


def create_new_directory(directoryName, directory_path, metadata):
    directory_pathList = get_directory_path_list(directory_path)
    curr = metadata
    
    # make sure the path is valid, traverse the path to the valid directory
    for directory in directory_pathList:
        if directory not in metadata.keys():
            return False
        else:
            curr = metadata[directory]
    # if valid, add the new directory in the metadata
    curr[directoryName] = {}
    
    # log the operation


# this is the function that you use to get chunkHandle according to number of chunks needed
def get_chunk_handle(number_of_chunks_needed, chunk_handle_counter_json):
    chunk_handler_dict = get_chunk_handlerCounter(chunk_handle_counter_json)
    chunk_hanlder = ChunkHandler(chunkHandleCounter=chunk_handler_dict["chunkHandleCounter"])
    handleList = create_chunk_handle(number_of_chunks_needed, chunk_hanlder, chunk_handle_counter_json)
    return handleList    


def get_chunk_size_needed(file_size):
    if file_size % 64 == 0:
        number_of_chunks_needed = file_size / 64
        return number_of_chunks_needed
    else:
        number_of_chunks_needed = int(file_size / 64) + 1
        return number_of_chunks_needed


def get_chunk_handlerCounter(chunk_handle_counter_json):
    chunkHandleCounterDict = {}
    with open(chunk_handle_counter_json) as f:
        chunkHandleCounterDict = json.load(f)
    return chunkHandleCounterDict


def update_chunk_handle_counter(hexNumber, chunk_handle_counter_json):
    data = get_chunk_handlerCounter(chunk_handle_counter_json)
    data["chunkHandleCounter"] = hexNumber
    data = json.dumps(data)
    with open(chunk_handle_counter_json, "w") as f:
        f.write(data)

def create_chunk_handle(number_of_chunks_needed, chunk_hanlder, chunk_handle_counter_json):
    handleList = []
    counter = None
    for i in range(number_of_chunks_needed):
        newHandle = chunk_hanlder.get_chunk_handle()
        counter = newHandle
        handleList.append(newHandle)
    update_chunk_handle_counter(counter, chunk_handle_counter_json)
    return handleList

def get_directory_path_list(directory_path):
    pathSlash = "/"
    return [pathSlash] + directory_path.split(pathSlash)[1:]


if __name__ == "__main__":
    # testing
    # r = get_chunk_handle(20, "chunkHandleCounter.json")
    # print(r)


"""
* getchunk- returns a list [chunkhandle, size, [replicas]]

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