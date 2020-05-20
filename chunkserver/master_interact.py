#master_interact.py - implementation of commands for interacting
#with the master
#Quang Tran - 05/16/2020

import os, datetime, random, math, json, logging

with open("config.json") as config_json:
    config = json.load(config_json)

def lease(chunk_handle: str) -> bool:
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
            if f.read(1) == b'\x00':
                return False
            else:
                #timedelta: https://docs.python.org/3/library/datetime.html#datetime.timedelta
                #https://stackoverflow.com/questions/1750644/how-to-use-python-to-calculate-time/48540232
                curr = datetime.datetime.now()
                f.seek(2)
                year = int.from_bytes(f.read(2), byteorder='big')
                month = int.from_bytes(f.read(1), byteorder='big')
                day = int.from_bytes(f.read(1), byteorder='big')
                hour = int.from_bytes(f.read(1), byteorder='big')
                minute = int.from_bytes(f.read(1), byteorder='big')
                second = int.from_bytes(f.read(1), byteorder='big')

                #logging.debug("{} {} {} {} {} {}".format(year, month, day, hour, minute, second))

                if year < curr.year or month < curr.month or day < curr.day:
                    f.seek(1)
                    f.write(b'\x00')
                    return False
                else: #same year, month and date, as last lease timestamp could not be from the future
                    curr_time = datetime.timedelta(hours = curr.hour,
                                                   minutes = curr.minute,
                                                   seconds = curr.second)
                    lease_time = datetime.timedelta(hours = hour,
                                                    minutes = minute,
                                                    seconds = second)
                    if (curr_time - lease_time).total_seconds() > config["LEASE_EXPIRE_SECONDS"]:
                        f.seek(1)
                        f.write(b'\x00')
                        return False
                    else:
                        return True

    except Exception as e:
        raise e

def chunk_inventory() -> dict:
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
        Key: "size" Value: size (size of the chunk minus the first 16 bytes)
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
            information = {'chunk_handle': '', 'mutating': '', 'lease': '', 'size': ''}

            chunk_handle = chunk.split('.')[0]
            information['chunk_handle'] = chunk_handle

            f.seek(0)
            if f.read(1) == '\x01':
                information['mutating'] = True
            else:
                information['mutating'] = False

            f.seek(2)
            lease_time = datetime.datetime(int.from_bytes(f.read(2), byteorder='big'), #year
                                           int.from_bytes(f.read(1), byteorder='big'), #month
                                           int.from_bytes(f.read(1), byteorder='big'), #day
                                           int.from_bytes(f.read(1), byteorder='big'), #hour
                                           int.from_bytes(f.read(1), byteorder='big'), #minute
                                           int.from_bytes(f.read(1), byteorder='big')) #second
            #https://www.w3docs.com/snippets/javascript/the-right-json-date-format.html
            #https://stackoverflow.com/questions/455580/json-datetime-between-python-and-javascript
            information['lease'] = lease_time.isoformat() + 'Z'
            information['size'] = os.path.getsize(config["CHUNK_PATH"] + chunk) - 9 #9 starting bytes

            f.close()

            chunk_inventory[chunk_handle] = information

        return chunk_inventory


    except Exception as e:
        raise e

def collect_garbage(deleted_chunks: list) -> bool:
    for chunk_handle in deleted_chunks:
        try:
            os.remove(config["CHUNK_PATH"] + chunk_handle + ".chunk")
        except Exception as e:
            logging.warning("OSError: {0} {1}".format(e.filename, e.strerror))
            raise e

    return True
