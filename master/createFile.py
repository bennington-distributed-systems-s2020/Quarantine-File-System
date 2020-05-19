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

def createNewFile(fileName, fileDirectory, fileSize, numberOfReplicas, chunkHandleCounterJson):
    if fileName is None:
        return False # could also pass error message with a tuple: (False, "fileName is empty")
    if fileDirectory is None:
        return False
    if fileSize is None or (fileSize < 0) or type(fileSize) != type(64):
        return False
    numberOfChunksNeeded = getChunkSizeNeeded(fileSize)
    chunkHandleList = getChunkHandle(numberOfChunksNeeded, chunkHandleCounterJson)
    getDirectoryPathPathList(fileDirectory)
    newFileMetadata = {}


def createNewDirectory(directoryName, directoryPath, metadata):
    directoryPathList = getDirectoryPathPathList(directoryPath)
    curr = metadata
    
    # make sure the path is valid, traverse the path to the valid directory
    for directory in directoryPathList:
        if directory not in metadata.keys():
            return False
        else:
            curr = metadata[directory]
    # if valid, add the new directory in the metadata
    curr[directoryName] = {}
    
    # log the operation


# this is the function that you use to get chunkHandle according to number of chunks needed
def getChunkHandle(numberOfChunksNeeded, chunkHandleCounterJson):
    chunkHandlerDict = getChunkHandlerCounter(chunkHandleCounterJson)
    chunkHandler = ChunkHandler(chunkHandleCounter=chunkHandlerDict["chunkHandleCounter"])
    handleList = createChunkhandle(numberOfChunksNeeded, chunkHandler, chunkHandleCounterJson)
    return handleList    


def getChunkSizeNeeded(fileSize):
    if fileSize % 64 == 0:
        numberOfChunksNeeded = fileSize / 64
        return numberOfChunksNeeded
    else:
        numberOfChunksNeeded = int(fileSize / 64) + 1
        return numberOfChunksNeeded

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

def getDirectoryPathPathList(directoryPath):
    pathSlash = "/"
    return [pathSlash] + directoryPath.split(pathSlash)[1:]

def isValidDirectoryPath(directoryPath, metadata):
    directoryPathList = getDirectoryPathPathList(directoryPath)
    currDirectory = metadata
    # make sure the path is valid, traverse the path to the valid directory
    for directory in directoryPathList:
        if directory not in metadata.keys():
            return False
        else:
            currDirectory = metadata[directory]
    # if valid, return the meata that points the valid directory path
    return currDirectory


if __name__ == "__main__":
    # testing
    # r = getChunkHandle(20, "chunkHandleCounter.json")
    # print(r)
    metadata = {
        "/":{
            "work":{
                "cs":{

                }
            }
        }
    }

    print(getDirectoryPathPathList("/work/cs"))
    s = isValidDirectoryPath("/work/cs",metadata)
    print(s)

"""

* getchunk- returns a list [chunkhandle, size, [replicas]]



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