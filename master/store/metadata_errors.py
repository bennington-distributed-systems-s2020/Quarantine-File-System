"""
 metadata_errors.py - Custom errors for missing chunks and files
                      chunkservers from a filename.
 Date: 5/17/2020
"""

class ChunkIndexError(Exception):
    def __init__(self, filename, index):
        super().__init__(f'{file} does not have a chunk at index number: {index}')

class FilenameKeyError(Exception):
    def __init__(self, filename):
        super().__init__(f'{file} does not exist in the metadata store')
