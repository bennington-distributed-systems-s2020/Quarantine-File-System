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


# Question to Client team: is chunk_index a string or intiger? 
@app.route('/fetch/<string:file_name>/<int:chunk_index>', methods=['GET'])
def fetch(file_name, chunk_index):
    if metadata_handler.verify_path(file_name) == False:
        return "invalid file path"
    
    # since this function takes a list of index, so I used [chunk_index] to make it a list
    json_response = {}
    chunk_info = get_file_chunk_handles(file_name, [chunk_index])[0]
    json_response["chunk_handle"] = chunk_info[0]   # extract chunk handle
    json_response["chunk_servers"] = chunk_info[2]  # extract replica locations
    return jsonify(json_response)
    
    """
    Caller: Client
    :param file_name: Name of the file being requested  
    :param chunk_index: A specific part of the file being requested 
    :return: chunk handle and chunk locations as JSON
    """

@app.route('/heartbeat', methods=['POST'])
def heartbeat():
    """
    Caller: Chunkserver
    :param state: Boolean value to check if a server is alive
    :return: Always "OK" with a status code of 200.
    """
    return "OK"


@app.route('/lease-request/<string:chunk_handle>', methods=['GET'])
def lease_request():
    """
    Caller: Chunkserver
    :param chunk_handle: Chunk handle in hex for a lease  
    :return: Boolean (True) if the operation succeeded 
    """
    return True
