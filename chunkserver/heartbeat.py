#!/usr/bin/python3

'''
heartBeat.py -- using a simple thread with Thread object to create a simple "HeartBea"t message, sent periodically from each chunkserver to the master to report status
Author: Sophia E Marx
Date: 05/18/2020

Editted to heartbeat.py by Quang Tran 05 23 20 mm dd yy
'''

#from threading import Thread
import time, json, requests

with open("config.json") as config_json:
    config = json.load(config_json)

with open("chunkserver.json") as chunkserver_json:
    chunkserver_config = json.load(chunkserver_json)

while True:
    state = False
    try:
        r = requests.get("http://localhost:8000", timeout=5)
        if r.status_code == 200:
            state = True
    except:
        state = False

    heartbeat = requests.get("http://{0}:{1}/heartbeat/{2}:{3}/{4}"
            .format(chunkserver_config["master"][0],
                    chunkserver_config["master"][1],
                    chunkserver_config["chunkserver"][0],
                    chunkserver_config["chunkserver"][1],
                    state))

    time.sleep(config["HEARTBEAT_DELAY"])

#class HeartBeat(Thread):
#
#    def __init__(self, chunk_handle, delay):
#        Thread.__init__(self)
#
#        self.chunk_handle = chunk_handle
#        self.delay = delay #currently using this to control the time between heartbeats
#
#    def print_status(self):
#        print(str(self.chunk_handle + " : Status: Alive and Kicking as of " + str(time.ctime())))
#        while True:
#            time.sleep(self.delay)
#            #I think we actually want to post a JSON here
#            print(str(self.chunk_handle + " : Status: Alive and Kicking as of " + str(time.ctime())))
#
#
#    def run(self):
#        print("Starting thread: " + str(self.chunk_handle))
#        self.print_status()
#        print("Finishing thread: " + str(self.chunk_handle))
#
#
#heartbeat = HeartBeat("fake chunkserver", 10)
#
#
#heartbeat.start()

#while True:
#    if not heartbeat.is_alive():
#        print("WE DIED")
#        break
