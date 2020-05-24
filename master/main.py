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
@app.route('/fetch/<string:file_path>/<string:command>/<int:chunk_index>', methods=['GET'])
def fetch(file_name, chunk_index):
    """
    Caller: Client
    :param file_name: Name of the file being requested  
    :param chunk_index: A specific part of the file being requested 
    :return: chunk handle and chunk locations as JSON
    """
    global metadata_handler
    if metadata_handler.verify_path(file_name) == False:
        error = {"error": "invalid file path"}
        return jsonify(error)
    # since this function takes a list of index, so I used [chunk_index] to make it a list
    json_response = {}
    chunk_info = get_file_chunk_handles(file_name, [chunk_index])[0]
    json_response["chunk_handle"] = chunk_info[0]   # extract chunk handle
    json_response["replica"] = chunk_info[2]  # extract replica locations
    return jsonify(json_response)
    

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
    update_live_chunk_server() # update available chunkserver, every 30s, runs forever