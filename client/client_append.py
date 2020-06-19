import requests, json, base64

with open("config.json", "r") as f:
    config_json = json.load(f)

def append(append_chunk, content):
    """
    append the content to the append_chunk. The format of append_chunk is that of a dictionary as detailed
    in the API for fetch.
    :param append_chunk: dictionary of chunk to append to with format like below:
        {
           chunk_handle: <handle of the chunk>,
           start_byte: <starting byte as calculated above>,
           primary: <ip address of the chunkserver with the primary chunk>,
           replica: [<address of replica1>, <address of replica2>,...]
        }
    :param content: base64 encoded string of the data to be appended
    :return: a tuple representing what the hell happened
        200: things went alright
        301: permanently moved aka run it again on the new chunk, the 2nd value is the remainin data to append
        400: abort with error code 400
        500: abort with error code 500
    """
    #pulling information
    chunk_handle = append_chunk["chunk_handle"]
    primary = append_chunk["primary"]
    replica = append_chunk["replica"]

    # 2) Break the data to 16mb chunks and send them to the replicas with the corresponding indices
    #converting back to bytes
    data = base64.decodebytes(content.encode())

    #slicing to 16mb blocks
    append_list = []
    chunk_size = config_json["MAX_APPEND_LIMIT"]
    for i in range(0, len(data), chunk_size):
        #re encoding as string
        data_base64_string = base64.encodebytes(data[i:i+chunk_size]).decode()
        append_list.append(data_base64_string)

    #sending to replicas
    for i in range(len(append_list)):
        #send to primary
        #if status code is not 200 exit
        if append_handle(primary, chunk_handle, append_list[i], i) != 200:
            return (500,)

        #send to replica
        for r in replica:
            if append_handle(r, chunk_handle, append_list[i], i) != 200:
                return (500,)

    # 3) Send append request to the primary once client has received acknowledgement from all replicas
    for i in range(len(append_list)):
        append_request_r = requests.post("http://{0}/append-request".format(primary),
                json={"chunk_handle": chunk_handle, "data_index": i})
        # if status code is 500 or we get return 3 => bad error happened. cancel operation and log
        if append_request_r.status_code == 500 or append_request_r.json() == 3:
            return (500,)
        # status code 400 means keyerror, ioerror or oserror, most of the time the file is not found
        elif append_request_r.status_code == 400 or append_request_r.json() == 1:
            return (400,)
        # chunk too full try on next chunk: call "ac" on master
        elif append_request_r.json() == 2:
            #constructing remaining data
            remaining = "".join(append_list[i:])
            print(remaining)
            return (301, remaining)

    #after everything is done return 200
    return (200,)

def append_handle(address, chunk_handle, data, index):
    append_r = requests.post("http://{0}/append".format(address),
            json= {"chunk_handle": chunk_handle, "data_index": index, "data": data})
    return append_r.status_code
