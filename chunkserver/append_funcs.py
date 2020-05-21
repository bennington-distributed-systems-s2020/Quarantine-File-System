#append_funcs.py - implementation of commands for appending
#Quang Tran - 05 20 20 mm dd yy

import os, datetime, random, math, json, logging, base64
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
    #Q: added CHUNK_PATH before the directory
    #Q: also moved the constants to the config.json
    #Q: I also changed the tab to 4 to avoid inconsistent TabError
    elif len(data) > config["CHUNK_SIZE"] - os.path.getsize(config["CHUNK_PATH"] + chunk_handle + ".chunk"):
        # FIXME: this logic should be moved to append_request see Nuclino API for more information
        return 2 # The operation failed because bytes > The amount of space left on the chunk
    else:
        # use the chunk_handle to create the cache file
        #Q: changed some code to write data as bytes
        with open(config["CHUNK_PATH"] + chunk_handle + '.chunk.' + str(datetime.datetime.now()) + 'cache', 'xb') as cache: # using x 'create only' mode so writing will fail if cache file already exists FIXME
            # dump the recieved bytes into the cache file
            #json.dump(data, cache)
            cache.write(data)
            return 0
    return 3 # ya--- idk

def append_request(chunk_handle: str) -> int:
    """
    Request to append the sent data. Note that the client shold only call
    this on the primary chunk.
        chunk_handle: str. The chunk handle of the chunk

    Return:
        int: An int denoting the status of the request.
            0: The operation succeeded.
            1: The operation failed because the requested chunk has no data in cache to append.
            2: The operation failed for other reasons.
    """
    return 2
