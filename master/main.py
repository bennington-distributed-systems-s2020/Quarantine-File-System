#!/usr/bin/env python3
"""
    main.py - Provides a Flask API to receive requests from both the client and chunkservers
    Date: 5/12/2020
"""

from flask import Flask, jsonify
from file_management import *

app = Flask(__name__)

@app.route("/")
def example():
    return "QFS master!"


# need to reform this function so that chunkserver can call and create new chunks or files
@app.route('/fetch/<string:file_name>/<int:chunk_index>', methods=['GET'])
def fetch(file_name, chunk_index):
    """
    Caller: Client
    :param file_name: Name of the file being requested  
    :param chunk_index: A specific part of the file being requested 
    :return: chunk handle and chunk locations as JSON
    """
    if metadata_handler.verify_path(file_name) == False:
        error = {"error": "invalid file path"}
        return jsonify(error)
    # since this function takes a list of index, so I used [chunk_index] to make it a list
    json_response = {}
    chunk_info = get_file_chunk_handles(file_name, [chunk_index])[0]
    json_response["chunk_handle"] = chunk_info[0]   # extract chunk handle
    json_response["replica"] = chunk_info[2]  # extract replica locations
    return jsonify(json_response)
    

@app.route('/heartbeat/<string: chunk_server_ip>/<bool: chunk_server_state>', methods=['POST'])
def heartbeat(chunk_server_ip,chunk_server_state):
    """
    Caller: Chunkserver
    :param chunk_server_ip: chunk_server_ip/dns
    :param chunk_server_state: bool, True(chunk server is available), False(unavailable) 
    :return: status code 200 means"OK"; code 500 means "error" 
    """
    try:
        metadata_handler.toggle(chunk_server_ip, chunk_server_state)
    except:
        return 500
    return 200


@app.route('/lease-request/<string:chunk_handle>', methods=['GET'])
def lease_request():
    """
    Caller: Chunkserver
    :param chunk_handle: Chunk handle in hex for a lease  
    :return: Boolean (True) if the operation succeeded 
    """
    return True

@app.route("/create/directory/<string:new_directory_path>")
def create_directory(new_directory_path = None):
    """
    caller: Chunkserver
    :param new_directory_path: the new directory's path. It has to be under an existing directory
    :return: 200 if operation succeeded; 400 if path is invalid
    :notice: directory path always ends with "/" to indicate it's directory
    :example: 1. if only "/" and, "/school/" exist, we call call create_directory ("/school/cs/")
                then it will be created and return 200. 
              2. now, if we call create_directory("/school/work/film/") this will return 400 means failed.
                because the "/school/work/" does not exist yet. we can only create directory under existing one.
    """
    if new_directory_path == None:
        return 400
    # call this function from file_management.py
    if create_new_directory(new_directory_path) == False:
        return 400
    else:
        return 200
    


@app.route("/create/file/<string:new_file_path>/<int:file_size>)
def create_file(new_file_path = None, file_size = 0):
    """
    caller: Chunkserver
    :param new_file_path: the new file's path. It has to be under an existing directory
    :param file_size: number of bytes of the file we creating
    :return: if succeed, return json format of all chunk handles for the file such as 
                    {"chunk handle": [chunk1_chunk_handle, chunk2_chunk_handle...]}
             if failed, return error in json if path invalid. such as {"error": 400}
    :example: 1. if "/school/" exist, we call call create_file("/school/fun.txt")
                        then it will be created and return all the chunk handles of this file
              2. if we call create_file("/school/work/film/fun.txt") this will return error mentioned above
                        because the /school/work/ does not exist yet. we can only create file under existing directory.
    """
    error = [{"error":"invalid file directory"}, {"error":"invalid file size"}]
    if verify_file_parent_directory_path(file_path) == False:
        return jsonify(error[0])
    elif type(file_size) != int or file_size < 0:
        return jsonify(error[1])
    # return the metadata of the created file in json format