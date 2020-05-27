#!/usr/bin/env python3
"""
 filemap.py - Structure that quickly returns chunkhandles and
              chunkservers from a filename.
 Date: 5/17/2020
"""

"""
The reason the FileMap and MetadataStore classes are broken up is because 
the FileMap class can be refactored to make things much faster later on
without complicating or breaking the interface with other components
"""


class FileMap:
    """
    Map of all of the metadata
    """
    def __init__(self, state = {}):
        self.files = {"":{}} if not state else state["files"]
        #each filename-> [[chunkhandle, size], [chunkhandle2, size], ...]
        self.chunkhandle_map = {} if not state else ["chunkhandles"]

    def process_path(self, path):
        if not type(path) == type('string'):
            return path
        else:
            return path.split("/") 

    def checkpoint(self):
        """
        Return state of the system as a dictionary.
        """
        return {
                "files":self.files, 
                "chunkhandles":self.chunkhandle_map
               }

    def retrieve(self, path, index):
        """
        Retrieve chunk
        """
        path = self.process_path(path)
        content = self.files
        for level in path:
            content = content[level]

        if index != None:
            chunk_info = [content[index]] + self.get_chunk_data(content[index])
            return chunk_info
        else:
            return [self.retrieve(path, chunk_index) for chunk_index in range(0, len(content[level]))]

    def add(self, path, index, chunkhandle, replicas = None, container = None):
        """
        Add or mutate a chunk
        """
        path = self.process_path(path)
        # print("path: {0}".format(path))
        if container == None: container = self.files
        # print("container: {0}".format(container))

        if len(path) == 1:
            self.change(chunkhandle, 0, replicas)
            # print("container path[0] {0}".format(container[path[0]]))
            for index in range(0, len(path)):
                container[path[0]].append(chunkhandle)
                return container

            else:
                # Append to chunk list if it doesn't exist
                container[path[0]] += [chunkhandle]
                return container
        else:
            container[path[0]] = self.add(path[1:], index, chunkhandle, replicas, container[path[0]])
            return container

    def change(self, chunkhandle, size = 0, replicas = None):
        if chunkhandle in self.chunkhandle_map:
            self.chunkhandle_map[chunkhandle][0] = size
        else:
            self.chunkhandle_map[chunkhandle] = [size, replicas]

    def make_path(self, path, top = True, directory = False, container = False):
        path = self.process_path(path)
        if top and len(path) == 1:
            return False
        elif top:
            directory = path[-1]==""

            if directory:
                if not self.verify_path(path[:-2]):
                    return False
                path = path[:-1]
            else:
                if not self.verify_path(path[:-1]):
                    return False
            self.files[path[0]] = self.make_path(path[1:], False, directory, self.files[path[0]])
            return True
        elif len(path) == 1:
            if path[0] in container:
                return False
            else:
                container[path[0]] = {} if directory else []
                return container
        else:
            content = self.make_path(path[1:], False, directory, container[path[0]])
            container[path[0]] = content
            return container
            
    def verify_path(self, path, container = False):
        path = self.process_path(path)
        if not container: container = self.files
        if len(path) == 2 and path[-1] == "":
            return path[0] in container
        elif len(path) == 1:
            return path[0] in container
        else:
            return self.verify_path(path[1:], container[path[0]])

    def remove(self, path, index = None, container = False):
        """
        Remove file or chunkhandles
        """
        path = self.process_path(path)
        print("path: {0}".format(path))
        content = self.files

        print("final content {0}".format(content))
        # print(content[path[-2]])

        # if removing a directory
        if index == None:
                # traverse to the parent directory and delete the directory
                for level in path[:-2]:
                    content = content[level]
                print("current content: {0}".format(content))
                del content[path[-2]]

        # remove a chunk according to chunk index
        else:
            # traverse to the file and delete the chunk
            for level in path[:-1]:
                content = content[level]
            # get chunk handle of the file, delete it in chunkhandle_map
            chunk_handle = self.retrieve(path, index)[0]
            del content[path[-1]]
            del self.chunkhandle_map[chunk_handle]
            
            
            
            
    #Add an active server or remove an inactive one
    def toggle(self, chunkserver, on):
        # This is slow right now, but I don't have an intelligent way
        # of mapping *cries*
        for chunkhandle in self.chunkhandle_map:
            if not on:
                if chunkserver in self.chunkhandle_map[chunkhandle]:
                    del self.chunkhandle_map[chunkhandle][chunkserver]
            else:
                if chunkserver not in self.chunkhandle_map[chunkhandle]:
                    self.chunkhandle_map[chunkhandle] += [chunkserver] 
                    

    def get_chunk_data(self, chunkhandle):
        return self.chunkhandle_map[chunkhandle]

    def list_chunkservers(self):
        """
        o(mn) where m is chunkservers and n is chunkhandles 
        *cries again*
        tbh, this is really o(n) since m is generally pretty small
        chunkhandles will usually have 3 or 4 chunkhandles so it's not
        really `m`
        """
        chunkservers=[]
        for chunkhandle in self.chunkhandle_map:
            for chunkserver in self.chunkhandle_map[chunkhandle]:
                if chunkserver not in chunkservers:
                    chunkservers += [chunkserver]
        return chunkservers


if __name__ == "__main__":
    # testing
    f = FileMap()
    f.make_path("/fun.txt")
    f.add("/fun.txt", -1,"fuckyou",["a"])
    a = f.retrieve("/fun.txt", 0)

    f.make_path("/school/")
    # def add(self, path, index, chunkhandle, replicas = None, container = None):
    f.make_path("/school/hello.txt")

    f.add("/school/hello.txt", 0, "chunkhanle", ["server","server2"])

    print(f.files)
    print(f.chunkhandle_map)
    print("\n")

    f.make_path("/school/music/")
    f.make_path("/school/music/hip-hop/")
    f.make_path("/school/music/trap/")
    print("after make path")
    print(f.files)
    print(f.chunkhandle_map)
    print("\n")


    f.remove("/school/music/trap/")
    print("after removing /trap/")
    print(f.files)
    print(f.chunkhandle_map)
    print("\n")

    f.remove("/school/music/")
    print("after removing /music/")
    print(f.files)
    print(f.chunkhandle_map)
    print("\n")


    f.remove("/fun.txt", 0)
    print("after removing the chunk in fun")
    print(f.files)
    print(f.chunkhandle_map)
    print("\n")
