#master_interact.py - implementation of commands for interacting
#with the master
#Quang Tran - 05/16/2020

import os, datetime, random, math, json

with open("config.json") as config_json:
    config = json.load(config_json)

def lease(chunk_handle: str):
    """
    Check whether the corresponding chunk_handle has a lease
    chunk_handle: str: A hexstring of the chunk_handle

    return: True if chunk has a lease, False if it does not or if
    the lease expired
    """
    try:
        with open(config["CHUNK_PATH"] + chunk_handle + '.chunk', 'rb+') as f:
            #check if the chunk has a lease. If yes, check if it has expired.
            f.seek(1)
            if f.read(1) == '0':
                #read here: https://stackoverflow.com/questions/35133318/return-bool-as-post-response-using-flask
                return json.dumps(False)
            else:
                #timedelta: https://docs.python.org/3/library/datetime.html#datetime.timedelta
                #https://stackoverflow.com/questions/1750644/how-to-use-python-to-calculate-time/48540232
                curr = datetime.datetime.now()
                f.seek(2)
                date = str(f.read(8))[2:-1]
                time = str(f.read(6))[2:-1]

                if int(date[0:4]) < curr.year or int(date[4:6]) < curr.month or int(date[6:8]) < curr.day:
                    f.seek(1)
                    f.write(b'0')
                    return False
                else: #same year, month and date, as last lease timestamp could not be from the future
                    curr_time = datetime.timedelta(hours = curr.hour,
                                                   minutes = curr.minute,
                                                   seconds = curr.second)
                    lease_time = datetime.timedelta(hours = int(time[0:2]),
                                                    minutes = int(time[2:4]),
                                                    seconds = int(time[4:6]))
                    if (curr_time - lease_time).total_seconds() > config["LEASE_EXPIRE_SECONDS"]:
                        f.seek(1)
                        f.write(b'0')
                        return False
                    else:
                        return True

    except Exception as e:
        raise e

def chunk_inventory():
    """
    Returns a dict containing information on a random subset of chunks on the chunkserver.
    The amount of chunks returned on random is determined based on the constant
    CHUNK_INVENTORY_RANDOM_SELECT * number of chunks

    Key: chunk_handle
    Value: dict
        Key: "chunk_handle" Value: chunk_handle
        Key: "mutating" Value: mutating (whether the file is being mutated)
        Key: "lease" Value: lease_timestamp (timestamp of the last timestamp
            the chunk has a lease. ISO 8601 format: "2010-04-20T20:08:21.634121")
    """
    try:
        #get the number of files to return
        no_files = math.ceil(config["CHUNK_INVENTORY_RANDOM_SELECT"] * len(os.listdir(config["CHUNK_PATH"])))
        #get the list of files to get information
        #https://pynative.com/python-random-sample/
        chunks_list = random.sample(os.listdir(config["CHUNK_PATH"]), no_files)

        chunk_inventory = {}

        for chunk in chunks_list:
            f = open(config["CHUNK_PATH"] + chunk, 'rb')
            information = {'chunk_handle': '', 'mutating': '', 'lease': ''}

            chunk_handle = chunk.split('.')[0]
            information['chunk_handle'] = chunk_handle

            f.seek(0)
            if f.read(1) == '1':
                information['mutating'] = True
            else:
                information['mutating'] = False

            f.seek(2)
            lease_time = datetime.datetime(int(float(f.read(4))), #year
                                           int(float(f.read(2))), #month
                                           int(float(f.read(2))), #date
                                           int(float(f.read(2))), #hour
                                           int(float(f.read(2))), #minute
                                           int(float(f.read(2)))) #second
            #https://www.w3docs.com/snippets/javascript/the-right-json-date-format.html
            #https://stackoverflow.com/questions/455580/json-datetime-between-python-and-javascript
            information['lease'] = lease_time.isoformat() + 'Z'

            chunk_inventory[chunk_handle] = information

        return chunk_inventory


    except Exception as e:
        raise e
