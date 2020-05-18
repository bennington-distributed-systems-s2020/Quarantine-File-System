"""
filename: createFile.py

functionality: Used for creating a new file for a client.
1. it assignes the new file

Date: May 17th, 2020
Author: Zhihong Li
"""
import json
import jsonify
from ChunkHandler import ChunkHandler


def create_new_file(fileName, folderPath, fileSize, numberOfReplicas):
    if fileName is None:
        return False
    if folderPath is None:
        return False
    if fileSize is None or (fileSize < 0) or type(fileSize) != type(64):
        return False

    numberOfChunksNeeded = getChunkSizeNeeded(fileSize)

    metadata = {}
    chunkHandler = ChunkHandler()
    

    
def getChunkSizeNeeded(fileSize):
    if fileSize % 64 == 0:
        numberOfChunksNeeded = fileSize / 64
        return numberOfChunksNeeded
    else:
        numberOfChunksNeeded = int(fileSize / 64) + 1
        return numberOfChunksNeeded

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