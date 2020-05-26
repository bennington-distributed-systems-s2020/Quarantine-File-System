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

    :return: a code representing what the hell happened
        200: things went alright
        301: permanently moved aka run it again on the new chunk
        400: abort with error code 400
        500: abort with error code 500
    """
    #2) Break the data to 16mb chunks and send them to the replicas with the corresponding indices
    #it's probably a good idea to wrap this part up in a function
    #so that it could easily be called again when we get an operation failed bc not enough space
    #in append request
    #UPDATE: it's also probably a good idea to wrap the entirety of append request as well

    #3) Send append request to the primary once client has received acknowledgement from all replicas
    #i'll build data index on top of this once ik how julian will handle data index in the above step
    append_request_r = requests.post("http://{0}/append-request".format(append_chunk["primary"]),
                                     json={json.dumps({"chunk_handle": append_chunk["chunk_handle"], "data_index": ""})})

    #if status code is 500 or we get return 3 => bad error happened. cancel operation and log
    if append_request_r.status_code() == 500 or append_request_r.json() == "3":
        return 500
    #status code 400 means keyerror, ioerror or oserror, most of the time the file is not found
    elif append_request_r.status_code() == 400 or append_request_r.json() == "1":
        return 400
    #chunk too full try on next chunk: call "ac" on master
    elif append_request_r.json() == "2":
        return 301
    #the only situation left is a success
    else:
        return 200
