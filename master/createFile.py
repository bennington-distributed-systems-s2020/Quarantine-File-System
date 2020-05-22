"""
file_name: createFile.py

functionality: Used for creating a new file for a client.
1. create_new_directory(directory_path)
here put absolute directory path such as "/school/work/"
You can only create one directory at an existing directory at a time

2. create_file(file_path, file_size)
file path eg: "/school/work/fun.txt"
file size: number of bytes of the file you wanna create and append data to.

3. create_new_chunk(file_path)
file path eg: "/school/work/fun.txt"
--it creates a new chunk for the file

4. remove_file(file_path, chunk_index)
file_path: could also be a file path "/school/work/fun.txt"
chunk_index: optional
---this function can remove a file or a certain chunk that holds the certain chunk index
---if chunk index is not given, this function will the whole file
---otherwise it only removes the chunk has the given index.


5. remove_directory(directory_path)
directory_path eg: "/school/work/"
this function will remove the directory "work" and everything in it
if it's valid.

Date: May 21th, 2020
Author: Zhihong Li
"""

import os
import json
from random import randint
from store import metadata

#############----Config---#################
number_of_replicas_json = "numberOfReplicasConfig.json"

# get chunk replicas
with open(number_of_replicas_json) as f:
    number_of_replicas = json.load(f)["numberOfReplicas"]

# get metadata_handler
metadata_handler = metadata.MetadataStorage.retrieveStorage()
####################################



def verify_file_parent_directory_path(file_path):
    global metadata_handler
    
    if type(file_path) != str or len(file_path) < 0:
        return False # invalid file_path
    # get file parent direcoty path
    parent_directory_path = get_file_parent_directory_path(file_path)

#################### need to check return value of the verify function of metadata_handler with FIVE#####################
   # check parent_directory_path directory exist, if not return False 
    if metadata_handler.verify_path(parent_directory_path) == True:
        return True
    else:
        return False


def get_file_parent_directory_path(file_path):
    parent_directory_path = file_path.split('/')[:-1]
    parent_directory_path = '/'.join(parent_directory_path) + '/'
    return parent_directory_path


def create_new_file(file_path, file_size):
    global metadata_handler
    global number_of_replicas
    # verify filesize
    if (file_size is None) or (type(file_size) != int) or (file_size < 0) :
        return False
    if verify_file_parent_directory_path(file_path) == False:
        return False
    number_of_chunks_needed = get_number_of_chunk_needed(file_size)

    # create new file with number of chunks needed in the metadata
    for _ in range(1, number_of_chunks_needed):
        # get random live server list according to number of replicas set in config
        live_servers_list = metadata_handler.locate()
        random_server_list = get_servers_list_that_stores_new_file(live_servers_list, number_of_replicas)
        
        # get chunk handle
        chunk_handle = metadata_handler.get_chunk_handle()
        # assign new chunks to different servers all the time. distribute chunks well
        metadata_handler.create_chunk(file_path, chunk_handle, random_server_list) #######verify if this function takes a list of chunkserver?
    return True # success

def create_new_directory(directory_path):
    global metadata_handler

    # get parent directory of the directoy path we creating.
    parent_directory_path = '/'.join(directory_path.split('/')[:-2]) + '/'

    # verify parent directory
    if verify_file_parent_directory_path(parent_directory_path) == False:
        return False ################## ask five about what the function returns.
    
    # if valid, add the new directory in the metadata
    metadata_handler.create_path(directory_path)
    return True # success

def create_new_chunk(file_path):
    global metadata_handler
    global number_of_replicas

    if metadata_handler.verify_path(file_path) == False:
        return False
    
    # get random chunkservers list to store the chunk
    live_chunkservers_list = metadata_handler.locate()
    new_chunk_hundle = metadata_handler.get_chunk_handle() ################## problem line no return value
    random_chunk_server_list = get_servers_list_that_stores_new_file(live_chunkservers_list, number_of_replicas)

    # create new chunk for chunkservers on the random list
    metadata_handler.create_chunk(file_path, new_chunk_hundle, random_chunk_server_list)  ######### ask takes a list of servers?
    return True # success

def remove_file(file_path):
    global metadata_handler
    if metadata_handler.verify_path(file_path) != True:
        return False # invalid path
    else:
        metadata_handler.remove(file_path) # remove the file
        return True

def remove_directory(directory_path):
    global metadata_handler

    # check if the directory is valid
    if metadata_handler.verify_path(directory_path) == False:
        return False # invalid directory
    
    # if valid, remove it
    metadata_handler.remove(directory_path)
    return True

# file size is in byte
def get_number_of_chunk_needed(file_size):
    if (type(file_size) != int) or file_size < 0:
        return False # wrong input return False
    one_mb = 1000000 # 1mb = 1000000 bytes
    chunk_size_offset = 16 
    one_chunk_size_in_byte = one_mb * 64 - chunk_size_offset

    if file_size % one_chunk_size_in_byte == 0:
        number_of_chunks_needed = file_size / one_chunk_size_in_byte
        return number_of_chunks_needed
    else:
        number_of_chunks_needed = int(file_size / one_chunk_size_in_byte) + 1
        return number_of_chunks_needed


def get_servers_list_that_stores_new_file(live_servers_list, number_of_replicas):
    live_servers_num = len(live_servers_list)
    random_server_list = []
    if live_servers_num <= 0:
        return False
    for _ in range(number_of_replicas):
        randomNum = randint(0,live_servers_num-1)
        random_server_list.append(live_servers_list[randomNum])
    return random_server_list




if __name__ == "__main__":
    # test get chunk size needed
    assert get_number_of_chunk_needed(-1) == False, "failed test"
    assert get_number_of_chunk_needed("19") == False, "failed test"
    assert get_number_of_chunk_needed(9999999999) == 157, "failed test"
    
    # test get chunk handle
    assert type(metadata_handler.get_chunk_handle()) == str, "Failed to get chunk handle"

    # test get live_server list from metadata object
    assert type(metadata_handler.locate()) == list, "failed to get live server list"

    # test creating new path
    assert metadata_handler.create_path("/school/") == """some success return value here""", "failed to create directory"
    assert metadata_handler.create_path("/school/cs/") == """some success return value here""", "failed to create directory"
    assert metadata_handler.create_path("/school/music/") == """some success return value here""", "failed to create directory"

    # test verify existing directory path
    assert metadata_handler.verify_path("/school/") == """some success return value here""", "failed to verify directory"
    assert metadata_handler.verify_path("/school/cs/") == """some success return value here""", "failed to verify directory"
    assert metadata_handler.verify_path("/school/music/") == """some success return value here""", "failed to verify directory"

    # test the method of getting directory's parent directory path
    parent_directory_path = '/'.join("/school/cs/".split('/')[:-2]) + '/'
    assert get_file_parent_directory_path("/school/cs/") == "/school/", "failed to get directory's parent directory path"

    # test creating a file
    assert create_new_file("school/cs/fun.txt", 10000000) == True, "failed to create file"
    assert create_new_file("school/cs/hello.txt", 50) == True, "failed to create file"
    assert metadata_handler.verify_path("school/cs/fun.txt") == True, "failed to remove a file"
    assert metadata_handler.verify_path("school/cs/hello.txt") == True, "failed to remove a file"

    # test create a new chunk for an existing file
    live_chunk_server_list = ["server1", "server2", "server3"]
    assert metadata_handler.create_chunk("school/cs/fun.txt","2299aac92", live_chunk_server_list) == True, "failed to create new chunk for existing file"

    # test getting a file's directory path
    assert get_file_parent_directory_path("school/cs/fun.txt") == "school/cs/", "failed to get file parent directory path"

    # test remove a directory
    assert metadata_handler.verify_path("school/music/") == True, "failed to get file parent directory path"
    assert metadata_handler.remove("school/music/") == True, "failed to get file parent directory path"
    assert metadata_handler.verify_path("school/music/") == False, "failed to get file parent directory path"

    # test remove a file
    assert metadata_handler.remove("school/cs/fun.txt") == True, "failed to remove a file"
    assert metadata_handler.verify_path("school/cs/fun.txt") == False, "failed to remove a file"

    # test remove a directory that has file in it
    assert metadata_handler.remove("school/cs/") == True, "failed to remove a directory that has file in it"
    assert metadata_handler.verify_path("school/cs/fun.txt") == False, "failed to remove a directory that has file in it"
    assert metadata_handler.remove("school/cs/") == False, "failed to remove a directory that has file in it"
