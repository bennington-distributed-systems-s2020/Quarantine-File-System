#!usr/bin/python3

'''
heartBeat.py -- using a simple thread with Thread object to create a simple "HeartBea"t message, sent periodically from each chunkserver to the master to report status
Author: Sophia E Marx
Date: 05/18/2020
'''

from threading import Thread
import time

class HeartBeat(Thread):

    def __init__(self, chunk_handle, delay):
        Thread.__init__(self)

        self.chunk_handle = chunk_handle
        self.delay = delay #currently using this to control the time between heartbeats

    def print_status(self):
        print(str(self.chunk_handle + " : Status: Alive and Kicking as of " + str(time.ctime())))
        while True:
            time.sleep(self.delay)
            #I think we actually want to post a JSON here
            print(str(self.chunk_handle + " : Status: Alive and Kicking as of " + str(time.ctime())))


    def run(self):
        print("Starting thread: " + str(self.chunk_handle))
        self.print_status()
        print("Finishing thread: " + str(self.chunk_handle))


heartbeat = HeartBeat("fake chunkserver", 10)


heartbeat.start()

while True:
    if not heartbeat.is_alive():
        print("WE DIED")
        break
