#master_interact.py - implementation of commands for interacting
#with the master
#Quang Tran - 05/16/2020

import datetime
from config import *

def lease(chunk_handle: str):
    """
    Check whether the corresponding chunk_handle has a lease
    chunk_handle: str: A hexstring of the chunk_handle

    return: True if chunk has a lease, False if it does not or if
    the lease expired
    """
    try:
        with open('./chunk/' + chunk_handle + '.chunk', 'rb+') as f:
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
                    if (curr_time - lease_time).total_seconds() > LEASE_EXPIRE_SECONDS:
                        f.seek(1)
                        f.write(b'0')
                        return False
                    else:
                        return True

    except Exception as e:
        raise e

