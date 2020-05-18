class ChunkIndexError(Exception):
    def __init__(self, filename, index):
        super().__init__(f'{file} does not have a chunk at index number: {index}')

class FilenameKeyError(Exception):
    def __init__(self, filename):
        super().__init__(f'{file} does not exist in the metadata store')
