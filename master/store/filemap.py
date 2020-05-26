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
        self.files = {} if not state else state["files"]
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

    def retrieve(self, path, index, container = False):
        """
        Retrieve chunk
        """
        if not container: container = self.files
        path = self.process_path(path)
        content = container[path[0]]
        if path.length() == 1:
            if index != None:
                return content[index] + [self.get_chunkservers(content[index][0])]
            else:
                result = []
                for chunk in content:
                    result += content[index] + \
                      [self.get_chunkservers(content[chunk][0])]
                return result
        else:
            return self.retrieve(path[1:], index, content)

    def update(self, path, index, value, replicas = False, container = False):
        """
        Add or mutate a chunk
        """
        if not container: container = self.files
        path = self.process_path(path)
        if path.length() == 1:
            # Update if the chunk exists
            if replicas: self.chunkhandle_map[value[0]] = replicas
            if content.length() - 1 <= index:
                if value.length() == 1:
                    content[index][1] = value
                else:
                    content[index] = value
                return content
            else:
                # Append to chunk list if it doesn't exist
                content[index] += [value]
                if replicas: self.chunkhandle_map[value[0]] = replicas
                return content
        else:
            content[path[0]] = self.update(path[1:], index, value, replicas, content[path[0]])
            return content

    def make_path(self, path, top = True, directory = False, container = False):
        path = self.process_path(path)
        if not container: container = self.files
        if top and path.length() == 1:
            return False
        elif top:
            return self.make_path(path[1:], False, path[-1]=="", container[path[0]])
        elif path.length() == 1:
            if path[0] in container:
                return False
            else:
                container[path] = {} if directory else []
                return container
        else:
            content =  self.make_path(path[1:], False, path[-1]=="", container[path[0]])
            return content
            
    def verify_path(self, path, container = False):
        path = self.process_path(path)
        if not container: container = self.files
        if path.length() == 1:
            return path[0] in container
        else:
            return self.verify_path(path[1:], content[path[0]])

    def remove(self, path, index = None, container = False):
        if not container:
            if self.verify_path(path):
                if path[-1] == "":
                    del path[-1]
                self.files = self.remove(path[1:],container=self.files[""])
                return True
            else:
                return False
        else:
            if path.length() <= 2:
                if index != None:
                    del container[path[0]][path[1]]
                else:
                    del container[path[0]][path[1]][index]
                return container
            else:
                container = self.remove(path[1:], index, container[path[0]])
                return container
                
                
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
                    

    def get_chunkservers(self, chunkhandle):
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


