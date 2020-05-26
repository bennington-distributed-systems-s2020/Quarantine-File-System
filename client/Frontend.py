#!/usr/bin/python3
#
# Frontend.py - Beginning of implementation of QFS client documentation
# Author: Rose/Roxy Lalonde {roseernst@bennington.edu}
# edited by ell 5/20/20
# Date created: 5/18/2020
# Some of the parameters in the functions might be part of the metadata.
# Perhaps the return from the metadata function should be to put the relevant data in a list,
# so that other functions can easily pull from it
#

from flask import Flask
from pip._vendor import requests

app = Flask(__name__)


@app.route("/")
def example():
    return "client flask API"


@app.route('/fetch/<string:file_name>/<int:chunk_index>')
def fetch(file_name, chunk_index):
    """
    Makes a request to the master for the metadata of a file. This will provide important
    information for the rest of the commands in this file.
    :param file_name: The name of the file to get metadata for
    :param chunk_index: translated from file name and byte offset specified by application
    :return: File metadata {error handle if nothing received or sanity checks failed}
    """
    metadata = 0  # Will have some kind of call to the master to get the metadata list
    return metadata


@app.route('/read/<string:file_name>,<int:chunk_handle>,<int:start_byte>,<int:byte_range>', method='GET')
def read(file_name, chunk_handle, start_byte, byte_range):
    """
    Reads out the requested file from the chunkserver
    :param file_name: Name of requested file
    :param chunk_handle: File ID
    :param start_byte: Where to start reading
    :param byte_range: How much to read
    :return: Text obtained from server
    """
    # Initialize some variables for error handling and return stuff
    output = 0

    # Wait for two minutes for the chunkserver to respond.
    while output == 0:
        # json = {chunk_handle: self.chunk_handle} was a parameter in Quang's example, but what is self?
        server_request = requests.get("http://{0}/read-request".format("URL"), timeout=90)

        # What function should I call to tell the server "hey give me stuff?"
        # output = {some call, does it need to have the parameters in ir or is that handled in the app route?}


        """
        for i in range(0, 12):
            if output != 0:
                break
            time.sleep(10)
            i = i + 1
        break
        """

    # Output things! As long as output has changed, the function should give the package from the chunkserver
    if output != 0:
        return output
    else:
        print("An error has occurred.")

    # Pass this all to the server, get back a status, and print a message to the user


@app.route('/write/<string:file_name>,<string:content>')
def write(file_name, content):
    """
    Writes a new file to the chunk server
    :param file_name: Name of file to be created
    :param content: What to write to the new file
    :return: Success confirmation or error message
    """
    # Pass this all to the server, get back a status, and print a message to the user


@app.route('/append/<string:file_name>,<string:content>,<int:chunk_handle>,<int:length>')
def append(file_name, content, chunk_handle, length):
    """
    Adds data to the end of a previously existing file
    :param file_name: Name of file to be appended to
    :param content: What to write to the end of the file
    :param chunk_handle: File ID
    :param length: The size in bytes of the data to be appended
    :return: Success confirmation or error message {documentation says boolean though?}
    """
    # Pass this all to the server, get back a status, and print a message to the user


@app.route('/append_request/<string:chunk_handle>')
def append_request(chunk_handle):
    """
    Asks the chunk server for permission to append to a file
    :param chunk_handle: File ID
    :return: Success confirmation or error message
    """
