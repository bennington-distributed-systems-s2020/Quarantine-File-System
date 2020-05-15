filename -> chunkhandle, size, lease
chunkhandle -> chunkservers

class FileMap:
    def __init__(self, state = {}):
        self.files = {} if not state else state["files"]
        self.chunkhandle_map = {} if not state else ["chunkhandle"]
        self.chunkservers = [] if not state else state["chunkservers"]

    def checkpoint(self):
        return {
                "files":self.info, 
                "chunkhandles":self.chunkhandle_map
                "chunkservers":self.chunkservers}

    def deactivate(self, chunkserver):
        del self.chunkservers["chunkservers"]

    def get_chunkservers(self, chunkhandle):
        pass

