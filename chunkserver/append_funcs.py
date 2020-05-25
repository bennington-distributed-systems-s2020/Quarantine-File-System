#append_funcs.py - implementation of commands for appending
#Quang Tran - 05 20 20 mm dd yy

import os, datetime, random, math, json, logging, fcntl, base64
import dateutil.parser

with open("config.json") as config_json:
    config = json.load(config_json)

#Julian Lambert - 05 20 20 mm dd yy
def append(chunk_handle: str, client_ip: str, data_index: str, data: str) -> int:
    """
    The Append function which takes data from the Client

    It expects JSON input from an HTTP POST request in the form: {
        'chunk_handle': <hex>,
		'data_index': <int>,
        'data': <binary_data>
    }

    It implements a gesture toward an LRU (Least Recently Used) Cache by overwriting buffer data when client sends more at the same index. Data is stored in a <chunk_handle>.<client_ip>.<data_index>.buffer file.

    It returns:
        - 0: Success: It worked
        - 1: Failure: Too many Bytes
        - 2: Failure: Yo idk
    """
    #Q: experimental conversaion of bytes encoded as a string using base64
    data = base64.decodebytes(data.encode())
    if len(data) > config["MAX_APPEND_LIMIT"]:
        return 1 # The operation failed because bytes > MAX_APPEND_LIMIT
    else:
        # use the chunk_handle, client_ip, and data_index to create the cache file
        #Q: changed some code to write data as bytes
        with open("{0}{1}.{2}.{3}.buffer".format(config["WRITE_BUFFER_PATH"], chunk_handle, client_ip, data_index), 'wb') as buffer: # using w 'open for writing, truncating the file first' mode so writing at the same index will overwrite old buffer data
            # dump the recieved data into the buffer file
            buffer.write(data)
            return 0
    return 2 # ya--- idk

def append_request(chunk_handle: str, client_ip: str, data_index: str) -> int:
    """
    Request to append the sent data. Note that the client shold only call
    this on the primary chunk.
        chunk_handle: str. The chunk handle of the chunk
        data_index int. The index of the client's append() call
    Return:
        int: An int denoting the status of the request.
            0: The operation succeeded.
            1: The operation failed because the requested chunk has no data in cache to append.
            2: The operation failed because the chunk is too full.
            3: The operation failed for other reasons.
    """
    #Format of filename for write buffer: <chunk_handle>.<client_ip>.chunktemp
    buffer_filename = config["WRITE_BUFFER_PATH"] + "{0}.{1}.{2}.buffer".format(chunk_handle, client_ip, data_index)
    chunk_filename = config["CHUNK_PATH"] + chunk_handle + ".chunk"

    #check if file exists
    try:
        append_file = open(buffer_filename, 'rb')
    except:
        return 1

    #check if write could be performed
    remaining_size = config["CHUNK_SIZE"] - os.path.getsize(chunk_filename)
    if os.path.getsize(buffer_filename) > remaining_size:
        os.remove(buffer_filename)
        return 2

    #time to logic
    #if primary: send request to replicas
    return_code = 0
    chunk_file = open(chunk_filename, 'ab+')

    #file locking: lock the chunk being appended to to not cause corruption
    #https://stackoverflow.com/questions/11853551/python-multiple-users-append-to-the-same-file-at-the-same-time
    #https://docs.python.org/3/library/fcntl.html#fcntl.flock
    fcntl.flock(chunk_file, fcntl.LOCK_EX)

    chunk_file.seek(1)
    if chunk_file.read(1) == b'\x01':
        #is primary
        try:
            #getting replicas
            with open('./replica.json', 'r+') as f:
                replica_json = json.load(f)
                replicas = replica_json[chunk_handle]

            #sending requests to replicas
            #possible improvement: multithread this
            for i in replicas:
                append_request = requests.post("http://{0}/append-request".format(i), json={'chunk_handle': chunk_handle, 'data_index': data_index})
                if append_request.status_code != 200:
                    return_code = 3
                    raise
                elif append_request.json() != 0:
                    return_code = append_request.json()
                    raise
                else:
                    continue

            #all replicas succeeded peacefully
            #time to append
            append_file(append_file, chunk_file)

        except:
            if return_code == 0:
                return_code = 3
    else:
        append_file(append_file, chunk_file)

    fcntl.flock(chunk_file, fcntl.LOCK_UN)
    append_file.close()
    chunk_file.close()

    #take off lease
    with open(chunk_filename, 'rb+') as chunk_file:
        chunk_file.seek(1)
        chunk_file.write(b'\x00')

    return return_code

#support function for appending from 1 file to another
def append_file(from_file, to_file):
    buffer_size = 1024
    #writing with buffer
    #from: https://stackoverflow.com/questions/16630789/python-writing-binary-files-bytes
    while True:
        buf = from_file.read(buffer_size)
        if buf:
            to_file.write(buf)
        else:
            break
