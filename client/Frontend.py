#!/usr/bin/python3
#
# Frontend.py - Beginning of implementation of QFS client documentation
# Author: Rose/Roxy Lalonde {roseernst@bennington.edu}
# edited by ell 5/20/20
# Date created: 5/18/2020
# Edited again by Roxy 5/26/20
#

from flask import Flask, json, jsonify, abort, request, Response
import requests
import client_append
import logging

logging.basicConfig(level=logging.DEBUG)

with open("client.json") as client_json:
    client_config = json.load(client_json)

app = Flask(__name__)

@app.route("/")
def example():
    return "client flask API"


# Will replace this with the fetch code called inside all of the other functions
# @app.route('/fetch/<string:file_name>/<int:chunk_index>')
# def fetch(file_name, chunk_index):
#    """
#    Makes a request to the master for the metadata of a file. This will provide important
#    information for the rest of the commands in this file.
#    :param file_name: The name of the file to get metadata for
#    :param chunk_index: translated from file name and byte offset specified by application
#    :return: File metadata {error handle if nothing received or sanity checks failed}
#    """
#    metadata = 0  # Will have some kind of call to the master to get the metadata list
#    #Q: Call fetch on master for this
#    if metadata = 0
#        programmer.cry(tears_of_profound_sadness)
#    else
#        return metadata

@app.route('/metadata', strict_slashes=False)
def metadata():
    #display metadata
    r = requests.get("http://{0}:{1}/metadata"
                     .format(client_config["master"][0], client_config["master"][1]))
    return r.json()

@app.route('/create/file/<path:file_path>')
def create_file(file_path):
    fetch_r = requests.get("http://{0}:{1}/create/file/{2}"
                             .format(client_config["master"][0], client_config["master"][1], file_path))

    if fetch_r.status_code == 500 or ("error" in fetch_r.json()):
        return Response("Exception on master when creating {0}: {1}"
                .format(file_path, fetch_r.json()["error"]), status=500)
    elif fetch_r.status_code != 200:
        app.logger.warning("Unknown error on Master when trying to create {0}".format(file_path))
        abort(500)
    else:
        return "OK"  # success

@app.route('/create/dir/<path:dir_path>')
def create_dir(dir_path):
    fetch_r = requests.get("http://{0}:{1}/create/directory/{2}"
                        .format(client_config["master"][0], client_config["master"][1], dir_path))
    if fetch_r.status_code == 500 or ("error" in fetch_r.json()):
        return Response("Exception on master when creating {0}: {1}"
                .format(dir_path, fetch_r.json()["error"]), status=500)
    elif fetch_r.status_code != 200:
        app.logger.warning("Unknown error on Master when trying to create {0}".format(dir_path))
        abort(500)
    else:
        return "OK"  # success

# Q: rewrote the spec for read. Note that the client does not have access to the metadata
# Q: It'd have to call fetch to the Master in order to get the chunkhandle to read from
@app.route('/read/<path:file_path>/<int:start_byte>/<int:byte_range>', methods=['GET'])
def read(file_path, start_byte, byte_range):
    """
    Reads out the requested file from the chunkserver
    :param file_name: Name of requested file
    :param start_byte: Where to start reading
    :param byte_range: How much to read
    :return: Text obtained from server
    """
    # Fetch things from the server.
    # Q: modified read to match api spec from master
    # Q: ignoring chunk index for now
    fetch_r = requests.get("http://{0}:{1}/fetch/{2}/{3}/{4}"
                            .format(client_config["master"][0], client_config["master"][1], file_path, "r", 0))
    if fetch_r.status_code == 500 or ("error" in fetch_r.json()):
        return Response("Exception on master when reading {0}: {1}"
                .format(file_path, fetch_r.json()["error"]), status=500)
    elif fetch_r.status_code != 200:
        app.logger.warning("Unknown error on Master when trying to read {0}".format(file_path))
        abort(500)
    else:
        #read on chunkserver
        chunks_list = fetch_r.json()
        output = ""
        for chunk in chunks_list:
            address = chunk[2][0]
            chunk_handle = chunk[0]
            #this will break on large files since there's no startbyte calculation
            read_r = requests.get("http://{0}/read".format(address),
                    json={"chunk_handle": chunk_handle, "start_byte": start_byte, "byte_range": byte_range})
            print(output)
            output += read_r.json()

        return output


@app.route('/write/<string:file_name>,<string:content>')
def write(file_name, content):
    """
    Writes a new file to the chunk server
    :param file_name: Name of file to be created
    :param content: What to write to the new file
    :return: Success confirmation or error message
    """
    # Pass this all to the server, get back a status, and print a message to the user
    abort(405)
    return ""


# modifying append and rewrite it to take in a json instead
# since it might not be a good idea to fit 16mb of content in an url
@app.route('/append/', strict_slashes=False, methods=['POST'])
def append():
    """
    Adds data to the end of a previously existing file
    :param file_name: Name of file to be appended to
    :param content: What to write to the end of the file
    :return: Success confirmation or error message {documentation says boolean though?}
    """
    # Pass this all to the server, get back a status, and print a message to the user
    # parsing json
    request_json = request.get_json()
    file_path = request_json["file_path"]
    content = request_json["content"]

    # Call fetch on Master to get the primary and the replicas
    fetch_r = requests.get("http://{0}:{1}/fetch/{2}/{3}"
                            .format(client_config["master"][0], client_config["master"][1], file_path, "a"), timeout = 10)
    # see API doc for return format
    append_chunk = fetch_r.json()[file_path]  # if fetch was done correctly this should just have 1 chunk in the list

    # call append
    return_tuple = client_append.append(append_chunk, content)
    return_code = return_tuple[0]
    # if we have to append again on a new chunk
    if return_code == 301:
        fetch_new_r = requests.get("http://{0}:{1}/fetch/{2}/{3}"
                                .format(client_config["master"][0], client_config["master"][1], file_path, "ac"))
        new_append_chunk = fetch_new_r.json()[file_path]
        # call the append function again on the new chunk
        return_code = client_append.append(new_append_chunk, return_tuple[1])

    # on a new chunk we could not get 301
    if return_code == 500:
        app.logger.critical("Exception on chunkserver {0}".format(append_chunk["primary"]))
        abort(500)
    elif return_code == 400:
        # what could cause this is unknown. We could attempt to run the func again ehre
        # though for now ill just log and abort
        app.logger.warning("Chunkhandle not found or buffer not found on chunkserver {0} or one of its replicas".format(
            append_chunk["primary"]))
        abort(400)
    else:
        return "OK"  # success
