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
    return "Flask!"


# need to reform this function so that chunkserver can call and create new chunks or files
# need a new parameter called command, start_byte
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
    
    # need to add chunk_primary into this return data. if it's r, w, or a operation.

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
