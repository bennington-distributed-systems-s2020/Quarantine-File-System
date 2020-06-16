#!/usr/bin/env python3
"""
    main.py - Provides a Flask API to receive requests from both the client and chunkservers
    Date: 5/12/2020

    Notice: all the path input from user do not requires the root "/". 
    for example: if we want to create a new directory called "school"
                    we can call "127.0.0.1/create/directory/school/" # notice directory has to end with '/'
                    here school is under directory "/" but user don't need to enter the root like "127.0.0.1/create/directory//school/
                
                 this applies to "create/file" "create/directory" and "fetch" end point
"""

import threading
from flask import Flask, jsonify
from file_management import *
from leases import *

app = Flask(__name__)


@app.route("/")
def example():
    return "QFS master!"


# need to do some change---should use metadata_handler.get_chunk(file_path), without index,
# you get all chunk info for the file. slice it up from there. return json

# need to reform this function so that chunkserver can call and create new chunks or files
@app.route('/fetch/<path:file_path>/<string:command>', methods=['GET', 'POST'])
@app.route('/fetch/<path:file_path>/<string:command>/<int:chunk_index>', methods=['GET', 'POST'])
def fetch(file_path, command, chunk_index=None):
    """
    Caller: Client
    :param file_path: path of the file. if you have a file under "/school/cs/" called work work.txt
                            then you should have "/school/cs/work/" # you can keep suffix of the file if you'd like
                            it's optional and it does not affect how you use our system.
    :param chunk_index: A specific part of the file being requested. 
                It's not needed when chunkserver is adding a new chunk to an existing file. 
    :return: if succeeds: chunk handle and chunk locations as JSON
                if fails: return error in json format {"error": "error messagesss"}
    """
    global metadata_handler
    file_path = "/" + file_path
    error = {"error": "invalid file path"}
    json_response = {}

    if metadata_handler.verify_path(file_path) == False:
        return jsonify(error)

    # return everything for the file
    if command == "r":
        # since this function takes a list of index, so I used [chunk_index] to make it a list
        chunk_info = metadata_handler.get_chunk(file_path)
        json_response[file_path] = chunk_info
        return jsonify(json_response)
    
    # return the last chunk of the file
    elif command == "a":
        global lease
        chunk_info = metadata_handler.get_chunk(file_path)[-1]
        
        # get chunk handle 
        chunk_handle = chunk_info[0]

        # grant lease
        output = lease.grant_lease(chunk_handle)

        json_response[file_path] = output

        return jsonify(json_response) # return json packaged chunk info
    
    # ac (append create). 
    # Create a new empty chunk for that file then return the address for that chunk.
    elif command == "ac":
        chunk_info = create_new_chunk(file_path)
        json_response[file_path] = chunk_info
        return jsonify(json_response)

@app.route('/create/file/<path:new_file_path>', methods = ['GET'])
def create_file(new_file_path):
    """
    Caller: Client
    :param new_file_path: path of the file being created 
    :param file_size: bytes of the file
    :return: all the chunk handles being created in json file under the key called "chunk_handle".  
                    don't know the exact format yet is in the value of the key yet, need to ask
    """
    global metadata_handler
    global live_chunk_server_dict
    new_file_path = "/" + new_file_path
    error = {"error": "something went wrong"}
    error_invalid_path = {"error": "invalid file path"}
    error_no_live_chunk_server = {"error": "there is no available chunkserver right now, please wait for a moment"}
    error_file_exists = {"error": "file already exists"}
    json_response = {"chunk_info": None}

    # check if there is any live chunkserver at all return error if none
    if len(live_chunk_server_dict) == 0:
        return jsonify(error_no_live_chunk_server)

    # verify file directory
    if verify_file_parent_directory_path(new_file_path) == False:
        return jsonify(error_invalid_path)

    try:
        if metadata_handler.verify_path(new_file_path) == True:
            return jsonify(error_file_exists)
        metadata_handler.create_path(new_file_path)
        result = create_new_chunk(new_file_path)
        if result == False:
            metadata_handler.remove(new_file_path)
            return jsonify(error_no_live_chunk_server)

        json_response["chunk_info"] = result

        # get chunk handle 
        chunk_handle = result[0]
        replicas = result[2]

        # create the file on all the chunkservers
        json_chunk_handle = {"chunk_handle": chunk_handle}
        for replica in replicas:
            r = requests.post("http://{0}/create".format(replica), json = json_chunk_handle)
            
        return jsonify(json_response)
    except:
        if metadata_handler.verify_path(new_file_path) == True:
            metadata_handler.remove(new_file_path)
        return jsonify(error)

@app.route('/create/directory/<path:new_directory_path>', methods = ['GET'])
def create_directory(new_directory_path):
    """
    Caller: Client
    :param new_directory_path: path of the directory will be being created
    :return: json file. if success, return {"success": "directory created"}
                    if failed, return {"error": "parent directory does not exist"}
    """
    new_directory_path = "/" + new_directory_path
    print("new directory path: ", new_directory_path)
    error = {"error": "invalid path"}
    success = {"success": "directory created"}
    output = create_new_directory(new_directory_path)
    if output == False:
        return jsonify(error)
    else:
        return jsonify(success)

@app.route('/remove/file/<path:file_path>')
def to_remove_file(file_path):
    file_path = "/" + file_path
    error_invalid_path = {"error": "invalid path"}
    error = {"error": "something went wrong"}
    success = {"success": "successfully removed the file {0}".format(file_path)}

    try:
        if remove_file(file_path) == False:
            return jsonify(error_invalid_path)
        return jsonify(success)
    except:
        return jsonify(error)    

@app.route('/remove/directory/<path:directory_path>')
def to_remove_directory(directory_path):
    directory_path = "/" + directory_path
    error_invalid_path = {"error": "invalid path"}
    error = {"error": "something went wrong"}
    success = {"success": "successfully removed the file {0}".format(directory_path)}

    try:
        if remove_directory(directory_path) == False:
            return jsonify(error_invalid_path)
        return jsonify(success)
    except:
        return jsonify(error)    

@app.route('/heartbeat/<string:chunk_server>/<string:chunk_server_state>', methods=['GET'])
def heartbeat(chunk_server,chunk_server_state):
    """
    Caller: Chunkserver
    :param chunk_server_ip: chunk_server_ip/dns
    :param chunk_server_state: string, True(chunk server is available), False(unavailable) 
    :return: status code 200 means"OK"; code 500 means "error" ; code 400 means invalid inputs
    """
    if chunk_server == None or chunk_server_state == None:
        return str(400)
    try:
        global live_chunk_server_dict
        chunk_server_state = chunk_server_state.lower()
        if chunk_server_state == "false":
            # remove from the set if its been set False
            if chunk_server in live_chunk_server_dict:
                del live_chunk_server_dict[chunk_server]

        elif chunk_server_state == "true":
            # if chunk_server in live_chunk_server_dict
            live_chunk_server_dict[chunk_server] = datetime.now()

        else:
            return "invalid statement"
    except:
        return str(500)
    return str(200)

@app.route('/lease-request/<string:chunk_handle>/<string:chunk_server_addr>/<int:chunk_size>', methods=['GET'])
def lease_request(chunk_handle, chunk_server_addr, chunk_size):
    """
    Caller: Chunkserver
    :param chunk_handle: Chunk handle in hex for a lease  
    :return: Boolean (True) if the operation succeeded 
    """
    global lease
    global metadata_handler
    metadata_handler.mutate_chunk(chunk_handle, chunk_size)
    if lease.grant_lease(chunk_handle, chunk_server_addr) == True:
        return lease.chunk_lease
    else:
        return False


@app.route('/liveserver', methods = ['GET'])
def live_server():
    """
    call this endpoint, it returns all liveserver for checking liveserver and debuging purpose.
    """
    global live_chunk_server_dict
    return jsonify(live_chunk_server_dict)


@app.route('/metadata')
def get_metadata():
    """
    call this endpoint, it returns the whole metadata as a json file for debugging purpose
    """
    global metadata_handler
    return jsonify(metadata_handler.store.files)


@app.route('/chunkinfo')
def get_chunk_info():
    """
    call this endpoint, it returns all the chunks info as a json file for debugging purpose
    """
    global metadata_handler
    return jsonify(metadata_handler.store.chunkhandle_map)


if __name__ == "__main__":
    # # test lease
    # lease.grant_lease("11","127.0.0.1")
    # output = "127.0.0.1"
    # assert lease.chunk_lease["11"]['primary'] == output, "lease grant failed"

    def flask_run():
        app.run(host='0.0.0.0')

    thread_update_live_server = threading.Thread(target=update_live_chunk_server) # update available chunkserver, every 30s, runs forever
    thread_app_run = threading.Thread(target=flask_run)
    thread_update_live_server.start()
    thread_app_run.start()


"""
take path as input in flask
https://flask.palletsprojects.com/en/1.1.x/quickstart/

multi-threading:
https://www.youtube.com/watch?v=IEEhzQoKtQU
"""
