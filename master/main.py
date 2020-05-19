#!/usr/bin/env python3
"""
    main.py - Provides a Flask API to receive requests from both the client and chunkservers
    Date: 5/12/2020
"""

from flask import Flask
from metadata import Metadata

app = Flask(__name__)

@app.route("/")
def example():
    return "Flask!"


# Question to Client team: is chunk_index a string or intiger?
@app.route('/fetch/<string:file_name>/<int:chunk_index>', methods=['GET'])
def fetch():
    """
    Caller: Client
    :param file_name: Name of the file being requested  
    :param chunk_index: A specific part of the file being requested 
    :return: chunk handle and chunk locations as JSON
    """
    return "..."


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
