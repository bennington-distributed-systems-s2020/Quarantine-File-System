#append_funcs.py - implementation of commands for appending
#Quang Tran - 05 20 20 mm dd yy

import os, datetime, random, math, json, logging, fcntl, base64
import dateutil.parser

with open("config.json") as config_json:
    config = json.load(config_json)

#Julian Lambert - 05 20 20 mm dd yy
def append(chunk_handle: str, data: str) -> int:
    """
    The Append function which takes data from the Client

    It expects JSON input from an HTTP POST request in the form: {
            'chunk_handle': <hex>,
            'bytes': <binary_data>
    }
    It implements a skeleton LRU (Least Recently Used) Cache but currently cached bytes have no expiration (FIXME). Bytes are stored in a <chunk_handle>.chunk.<timestamp>.cache file

    It returns:
            - 0: Success: It worked
            - 1: Failure: Too many Bytes
            - 2: Failure: Chunk too full
            - 3: Failure: Yo idk
    """
    #bytes = request_json['bytes'] # FIXME should typecast as bytes
    #Q: experimental conversaion of bytes encoded as a string using base64
    data = base64.decodebytes(data.encode())
    if len(data) > config["MAX_APPEND_LIMIT"]:
        return 1 # The operation failed because bytes > MAX_APPEND_LIMIT
    #Q: added WRITE_BUFFER_PATH to separate the directory for storing the buffer path from the chunks dir
    #Q: also moved the constants to the config.json
    #Q: I also changed the tab to 4 to avoid inconsistent TabError
    elif len(data) > config["CHUNK_SIZE"] - os.path.getsize(config["WRITE_BUFFER_PATH"] + chunk_handle + ".chunk"):
        # FIXME: this logic should be moved to append_request see Nuclino API for more information
        return 2 # The operation failed because bytes > The amount of space left on the chunk
    else:
        # use the chunk_handle to create the cache file
        #Q: changed some code to write data as bytes
        with open(config["WRITE_BUFFER_PATH"] + chunk_handle + '.chunk.' + str(datetime.datetime.now()) + 'cache', 'xb') as cache: # using x 'create only' mode so writing will fail if cache file already exists FIXME
            # dump the recieved bytes into the cache file
            #json.dump(data, cache)
            cache.write(data)
            return 0
    return 3 # ya--- idk

def append_request(chunk_handle: str, client_ip: str) -> int:
    """
    Request to append the sent data. Note that the client shold only call
    this on the primary chunk.
        chunk_handle: str. The chunk handle of the chunk

    Return:
        int: An int denoting the status of the request.
            0: The operation succeeded.
            1: The operation failed because the requested chunk has no data in cache to append.
            2: The operation failed because the chunk is too full.
            3: The operation failed for other reasons.

3. Send the serialization to replicas (I'll have to update the API to have a specific append-request command that takes in a serialization that should only be called from a chunkserver to another chunkserver probably)
4. Check if write could be performed on replicas
  4.1. If no, wipe write buffer and send cancel signal to primary, which will also wipe its buffer and cancel the write
  4.2. If yes, continue
5. Write the data on the replicas then send acknowledgement back to primary
6. Once primary received acks from all replicas, write on primary
7. Send acks back to client and complete the append
    """
    #Format of filename for write buffer: <chunk_handle>.<client_ip>.chunktemp
    buffer_filename = config["WRITE_BUFFER_PATH"] + "{0}.{1}.chunktemp".format(chunk_handle, client_ip)
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
    success = True
    chunk_file = open(chunk_filename, 'ab+')

    #file locking: lock the chunk being appended to to not cause corruption
    #https://stackoverflow.com/questions/11853551/python-multiple-users-append-to-the-same-file-at-the-same-time
    #https://docs.python.org/3/library/fcntl.html#fcntl.flock
    fcntl.flock(chunk_file, fcntl.LOCK_EX)

    chunk_file.seek(1)
    if chunk_file.read(1) == b'\x01':
        #is primary
        try:
            #send requests to replica
            append_file(append_file, chunk_file)
        except:
            success = False
    else:
        append_file(append_file, chunk_file)

    fcntl.flock(chunk_file, fcntl.LOCK_UN)
    append_file.close()
    chunk_file.close()

    #take off lease
    with open(chunk_filename, 'rb+') as chunk_file:
        chunk_file.seek(1)
        chunk_file.write(b'\x00')

    if success:
        return 0
    else:
        return 3

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
