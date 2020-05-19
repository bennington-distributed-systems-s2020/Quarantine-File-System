"""
File name: ChunkHandle.py

Functionality:
contains the class called ChunkHandler which return a string version immutable
and globally Unique 28 bytes hex chunk handle no inputs required. It increase
the handle hex by 0x1 everytime a new chunk is returned.

variables:
chunkHandleCounter: the counter is created for increment purpose. default 0x0
maxChunkHandleHex: created for configuring the max handle hex. default 28bytes max hex

return value eg:
if the Hex is 0x11A, the function will return string type '11A'. it cuts off 0x for naming
the chunk purpose.


Date: May 17th, 2020
Author: Zhihong Li
"""
class ChunkHandler:
    def __init__(self, chunkHandleCounter=0x0, maxChunkHandleHex = 0x3fffffff):
        self.chunkHandleCounter = chunkHandleCounter
        self.convertStrToHex()
        self.maxChunkHandleHex = maxChunkHandleHex

    def get_chunk_handle(self):
        if type(self.chunkHandleCounter) == str:
            self.chunkHandleCounter = int(self.chunkHandleCounter, 16)

        if self.chunkHandleCounter < self.maxChunkHandleHex:
            self.chunkHandleCounter += 1
            self.chunkHandleCounter = hex(self.chunkHandleCounter)
            if type(self.chunkHandleCounter) == str:
                return self.chunkHandleCounter[2:]
            else:
                return self.chunkHandleCounter
        else:
            return False

    def convertStrToHex(self):
        if type(self.chunkHandleCounter) == str:
            strHex = "0x" + self.chunkHandleCounter
            num = int(strHex, 16)
            self.chunkHandleCounter = hex(num)

    def __str__(self):
        return hex(self.chunkHandleCounter)[2:]

    
if __name__ == "__main__":
    # testing
    h = ChunkHandler()
    for i in range(10):
        output = h.get_chunk_handle()
        print(output)


"""
reference:
hex calculation in python:
https://www.reddit.com/r/learnpython/comments/3birjt/is_there_a_way_to_do_math_in_hex_without/


>>> sys.getsizeof(0x3fffffff) // 28  max hex number for 28 byte int
>>> int('0x3fffffff', 16) // 1073741823 max int for 28 byte int

"""
