#!/usr/bin/env python3
"""
    main.py - Provides a Flask API to receive requests from both the client and chunkservers
    Date: 5/12/2020
"""

import threading
from flask import Flask, jsonify
from file_management import *

app = Flask(__name__)

@app.route("/")
def example():
    return "QFS master!"


# need to reform this function so that chunkserver can call and create new chunks or files
@app.route('/fetch/<string:file_path>/<int:chunk_index>', methods=['GET'])
def fetch(file_path, command, chunk_index):
    """
    Caller: Client
    :param file_name: Name of the file being requested  
    :param chunk_index: A specific part of the file being requested 
    :return: chunk handle and chunk locations as JSON
    """
    global metadata_handler
    error = {"error": "invalid file path"}
    json_response = {}

    if metadata_handler.verify_path(file_path) == False:
        return jsonify(error)

    # since this function takes a list of index, so I used [chunk_index] to make it a list
    chunk_info = get_file_chunk_handles(file_path, [chunk_index])[0]

    json_response["chunk_handle"] = chunk_info[0]   # extract chunk handle
    json_response["replica"] = chunk_info[2]  # extract replica locations
    return jsonify(json_response)
    
@app.route('/create/file/<string:new_file_path>/<int:file_size>')
def create_file(new_file_path, file_size):
    """
    Caller: Client
    :param new_file_path: path of the file being created 
    :param file_size: bytes of the file
    :return: all the chunk handles being created in json file under the key called "chunk_handle".  
                    don't know the exact format yet is in the value of the key yet, need to ask
    """
    error = {"error": "invalid file path"}
    json_response = {}
    output = create_new_file(new_file_path, file_size)
    if output == False:
        return jsonify(error)
    else:
        json_response["chunk_handle"] = output
        return jsonify(json_response)


@app.route('/create/directory/<string:new_directory_path>')
def create_directory(new_directory_path):
    """
    Caller: Client
    :param new_directory_path: path of the directory will be being created
    :return: json file. if success, return {"success": "directory created"}
                    if failed, return {"error": "parent directory does not exist"}
    """
    error = {"error": "parent directory does not exist"}
    success = {"success": "directory created"}
    output = create_new_directory(new_directory_path)

    if output == False:
        return jsonify(error)
    else:
        return jsonify(success)


@app.route('/heartbeat/<string: chunk_server>/<bool: chunk_server_state>', methods=['POST'])
def heartbeat(chunk_server,chunk_server_state):
    """
    Caller: Chunkserver
    :param chunk_server_ip: chunk_server_ip/dns
    :param chunk_server_state: bool, True(chunk server is available), False(unavailable) 
    :return: status code 200 means"OK"; code 500 means "error" ; code 400 means invalid inputs
    """
    if chunk_server == None or chunk_server_state == None:
        return 400
    try:
        global live_chunk_server_set
        global metadata_handler
        metadata_handler.toggle(chunk_server, chunk_server_state)
        if chunk_server_state == False:
            live_chunk_server_set.remove(chunk_server)
        elif chunk_server_state == True:
            live_chunk_server_set.add(chunk_server)
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


if __name__ == "__main__":
    thread_update_live_server = threading.Thread(target=update_live_chunk_server) # update available chunkserver, every 30s, runs forever
    app_run = threading.Thread(target=app.run)

    thread_update_live_server.start()
    app_run.start()