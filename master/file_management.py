"""
file_name: file_management.py
Date: May 22th, 2020
Author: Zhihong Li

Notice: a. all directory path starts from base directory "/"
        b. all directory path ends with "/" for example: "/school/"
                under base "/" directory, the directory "school" ends with "/"
        
functionality: Used for creating a new file for a client.
1. create_new_directory(directory_path)
here put absolute directory path such as "/school/work/"
You can only create one directory at an existing directory at a time

2. create_new_file(file_path, file_size)
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

6. get_file_chunk_handles(file_path, chunk_index_list)
file_path eg: "/school/work/cs/tree.py"
chunk_index_list eg: [0] or [0,1,2,3] or [3,5,7,8,9,22]
"""

import json
from random import randint
from store import metadata
from time import sleep
from datetime import datetime

#############----Config---#################
number_of_replicas_json = "numberOfReplicasConfig.json"

# get chunk replicas
with open(number_of_replicas_json) as f:
    number_of_replicas = json.load(f)["numberOfReplicas"]

# get metadata_handler##########################TODO: fix this
metadata_handler = metadata.MetadataStorage.retrieve_storage()

live_chunk_server_set = set()
####################################


def update_live_chunk_server():
    global live_chunk_server_set
    while True:
        # after 30s if chunkserver did not heartbeat master, we will remove
        # the chunkserver from available chunkserver list.
        # live_chunk_server_set stored a list of tupple like: (chunkserver, datetime_heard_heartbeat)
        sleep(30)
        now = datetime.now()
        to_remove_list = []
        for chunk_server, datetime_heard_heartbeat in live_chunk_server_set:
            if (datetime_heard_heartbeat - now).second > 30:
                to_remove_list.append((chunk_server, datetime_heard_heartbeat))
        
        for i in range(len(to_remove_list)):
            live_chunk_server_set.remove(to_remove_list[i])
        

def verify_file_parent_directory_path(file_path):
    global metadata_handler
    
    if type(file_path) != str or len(file_path) < 0:
        return False # invalid file_path
    # get file parent direcoty path
    parent_directory_path = get_file_parent_directory_path(file_path)

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
    global live_chunk_server_set
    # verify filesize
    if (file_size is None) or (type(file_size) != int) or (file_size < 0) :
        return False
    if verify_file_parent_directory_path(file_path) == False:
        return False
    number_of_chunks_needed = get_number_of_chunk_needed(file_size)

    # create new file with number of chunks needed in the metadata
    for _ in range(number_of_chunks_needed): 
        # get random live server list according to number of replicas set in config
        random_chunk_server_list = get_servers_list_that_stores_new_file(live_chunk_server_set, number_of_replicas)
        
        # get chunk handle
        chunk_handle = metadata_handler.get_chunk_handle()
        # assign new chunks to different servers all the time. distribute chunks well
        metadata_handler.create_chunk(file_path, chunk_handle, random_chunk_server_list) #takes a list of chunkserver
        
    try:
        output = metadata_handler.get_chunk(chunk_handle)
        return output
    except:
        return {"error": "failed to grab chunk"}

def create_new_directory(directory_path):
    global metadata_handler

    # get parent directory of the directoy path we creating.
    parent_directory_path = '/'.join(directory_path.split('/')[:-2]) + '/'

    # verify parent directory
    if verify_file_parent_directory_path(parent_directory_path) == False:
        return False 
    
    # if valid, add the new directory in the metadata
    metadata_handler.create_path(directory_path)
    return True # success

def create_new_chunk(file_path):
    global metadata_handler
    global number_of_replicas
    global live_chunk_server_set

    if metadata_handler.verify_path(file_path) == False:
        return False
    
    # get random chunkservers list to store the chunk
    new_chunk_hundle = metadata_handler.get_chunk_handle() 
    random_chunk_server_list = get_servers_list_that_stores_new_file(live_chunk_server_set, number_of_replicas)

    # create new chunk for chunkservers on the random list
    metadata_handler.create_chunk(file_path, new_chunk_hundle, random_chunk_server_list)
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


def get_servers_list_that_stores_new_file(live_servers_tuple_set, number_of_replicas):
    live_servers_num = len(live_servers_tuple_set)
    live_chunk_server_list= []
    random_server_list = []
    if live_servers_num <= 0:
        return False
    
    for chunk_server, timestamp in live_servers_tuple_set:
        live_chunk_server_list.append(chunk_server)
        
    for _ in range(number_of_replicas):
        randomNum = randint(0,live_servers_num-1)
        random_server_list.append(live_chunk_server_list[randomNum])
    return random_server_list


def get_file_chunk_handles(file_path, chunk_index_list):
    global metadata_handler

    if metadata_handler.verify_path(file_path) != True:
        return False # invalid file_path
    if (chunk_index_list == None) or (type(chunk_index_list) != list) or (len(chunk_index_list) <= 0):
        return False # invalid chunk_index_list
    chunk_handles = []
    chunk_index_list_len = len(chunk_index_list)

    for i in range(chunk_index_list_len):
        curr_chunk_index = chunk_index_list[i]
        curr_chunk_handle = metadata_handler.get_chunk(file_path, curr_chunk_index)
        chunk_handles.append(curr_chunk_handle)
    return chunk_handles


if __name__ == "__main__":
    # test get random live server function
    live_server = {(3, 3), (1, 1), (2, 2)}
    o = get_servers_list_that_stores_new_file(live_server, 1)
    print(o)

    # test get chunk size needed
    assert get_number_of_chunk_needed(-1) == False, "failed test"
    assert get_number_of_chunk_needed("19") == False, "failed test"
    assert get_number_of_chunk_needed(9999999999) == 157, "failed test"
    
    # test get chunk handle
    assert type(metadata_handler.get_chunk_handle()) == str, "Failed to get chunk handle"

    # test get live_server list from metadata object
    assert type(metadata_handler.locate()) == list, "failed to get live server list"

    # test creating new path
    assert metadata_handler.create_path("/school/") == None, "failed to create directory"
    assert metadata_handler.create_path("/school/cs/") == None, "failed to create directory"
    assert metadata_handler.create_path("/school/music/") == None, "failed to create directory" # here since the function is not returning anything

    # test verify existing directory path
    assert metadata_handler.verify_path("/school/") == True, "failed to verify directory"
    assert metadata_handler.verify_path("/school/cs/") == True, "failed to verify directory"
    assert metadata_handler.verify_path("/school/music/") == True, "failed to verify directory"

    # test the method of getting directory's parent directory path
    parent_directory_path = '/'.join("/school/cs/".split('/')[:-2]) + '/'
    assert get_file_parent_directory_path("/school/cs/") == "/school/", "failed to get directory's parent directory path"

    # test creating a file
    assert create_new_file("school/cs/fun.txt", 10000000) == True, "failed to create file"
    assert create_new_file("school/cs/hello.txt", 50) == True, "failed to create file"
    assert metadata_handler.verify_path("school/cs/fun.txt") == True, "failed to remove a file"
    assert metadata_handler.verify_path("school/cs/hello.txt") == True, "failed to remove a file"

    # test mutate chunk size
    metadata_handler.mutate_chunk("school/cs/hello.txt", 0, 1000)
    assert metadata_handler.get_chunk("school/cs/hello.txt", 0)[1] == 1000, "failed to mutate chunk size"

    # test get file chunk handles
    fun_chunk_handle = get_file_chunk_handles("school/cs/fun.txt", [0])
    hello_chunk_handle = get_file_chunk_handles("school/cs/hello.txt", [0]) # get first index 0 chunk handle for the hello.txt
    assert hello_chunk_handle == "2", "failed to get correct chunk handle for the file"
    assert fun_chunk_handle == "1", "failed to get correct chunk handle for the file"

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

