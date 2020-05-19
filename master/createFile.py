"""
filename: createFile.py

functionality: Used for creating a new file for a client.
1. it assignes the new file

Date: May 17th, 2020
Author: Zhihong Li
"""
import json
from ChunkHandler import ChunkHandler
import os

def create_new_file(fileName, fileDirectory, fileSize, numberOfReplicas, chunkHandleCounterJson):
    if fileName is None:
        return False
    if fileDirectory is None:
        return False
    if fileSize is None or (fileSize < 0) or type(fileSize) != type(64):
        return False

    numberOfChunksNeeded = getChunkSizeNeeded(fileSize)

    newFileMetadata = {}

    
def getChunkSizeNeeded(fileSize):
    if fileSize % 64 == 0:
        numberOfChunksNeeded = fileSize / 64
        return numberOfChunksNeeded
    else:
        numberOfChunksNeeded = int(fileSize / 64) + 1
        return numberOfChunksNeeded


def getFileDirectoryPathList(fileDirectory):
    return ["/"] + fileDirectory.split("/")[1:]


def getChunkHandlerCounter(chunkHandleCounterJson):
    chunkHandleCounterDict = {}
    with open(chunkHandleCounterJson) as f:
        chunkHandleCounterDict = json.load(f)
    return chunkHandleCounterDict

def updateChunkHandleCounter(hexNumber, chunkHandleCounterJson):
    data = getChunkHandlerCounter(chunkHandleCounterJson)
    data["chunkHandleCounter"] = hexNumber
    data = json.dumps(data)
    with open(chunkHandleCounterJson, "w") as f:
        f.write(data)


def createChunkhandle(numberOfChunksNeeded, chunkHandler, chunkHandleCounterJson):
    handleList = []
    counter = None
    for i in range(numberOfChunksNeeded):
        newHandle = chunkHandler.get_chunk_handle()
        counter = newHandle
        handleList.append(newHandle)
    updateChunkHandleCounter(counter, chunkHandleCounterJson)
    return handleList


# this is the function that you use to get chunkHandle according to number of chunks needed
def getChunkHandle(numberOfChunksNeeded, chunkHandleCounterJson):
    currentPath = (os.getcwd() + os.sep + "master")
    os.chdir(currentPath)
    chunkHandlerDict = getChunkHandlerCounter(chunkHandleCounterJson)
    chunkHandler = ChunkHandler(chunkHandleCounter=chunkHandlerDict["chunkHandleCounter"])
    handleList = createChunkhandle(numberOfChunksNeeded, chunkHandler, chunkHandleCounterJson)
    return handleList


if __name__ == "__main__":
    r = getChunkHandle(20, "chunkHandleCounter.json")
    print(r)    





"""
Inputs: 
file name
folder Path (namespace)
fileSize(unit MB)
 
What happens in the function:
Get number of chunks needed for the file
create file metadata (namespace, chunks with handles)
Assign three chunkservers to own the file. (chunkservers that holds the file namespace and chunks)
Create metadata for the new file (includes file namespace:chunks(with index) and handles, chunkservers
that holds it)
Append new metadata and namespace to the namespace-metadata map file
Assign a primary for all the chunks and return it and all other replicas locations. (maybe chunkservers 
that holds the chunks) because the client will ask the chunkserver for access and write or read. If 
chunkserver is not primary, they will ask us for it. (might be some special cases here)

"""