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

        # print("path: {0}".format(path))
        c = 0
        # print("content: {0}".format(content))
        for level in path:
            c += 1
            # print(c)
            content = content[level]
            # print(c)
            # print("level: {0}".format(level))
            # print(type(level))
            # print("content: {0}".format(content))
        
        if index != None:
            chunk_info = [content[index]] + self.get_chunk_data(content[index])
            return chunk_info
        else:
            # return [self.retrieve(path, chunk_index) for chunk_index in range(0, len(content[level]))]
            return [[chunk] + self.get_chunk_data(chunk) for chunk in content]

    ########################### rewrite it if this function does not work well after more testing
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
            if index in range(0, len(path)):
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

    def make_path(self, path):
        path = self.process_path(path)
        # print("path: ", path)
        # handle cases when user only enters one character
        if len(path) == 1 and path[0] != "":
            return False
        elif len(path) == 1 and path[0] == "":
            return True

        # handle directory creation
        if path[-1] == "":
            # traverse to parent directory and create new directory
            parent_directory_list = path[:-2]
            new_directory = path[-2]
            curr = self.files

            try:
                for direcotory in parent_directory_list:
                    curr = curr[direcotory]
                # now we add new directory to the metadata
                curr[new_directory] = {}
                # print("files: ", self.files)
                return True
            except:
                return False

        # handle file creation
        if path[-1] != "":
            parent_directory_list = path[:-1]
            new_file_name = path[-1]
            curr = self.files
            # traverse to the parent directory:
            try:
                for direcotory in parent_directory_list:
                    curr = curr[direcotory]
                # add the file path in metadata
                curr[new_file_name] = []
                # print("files: ", self.files)
                return True
            except:
                return False
            
    def verify_path(self, path, container = False):
        path = self.process_path(path)
        if not container: container = self.files
        
        # travese til the end, if anything does not exist, return false. 
        # if it's a directory, traverse there return true
        if path[-1] == "":
            try:
                content = container
                for level in path[:-1]:
                    content = content[level]
                return True
            except:
                return False
        # if it's a file, traverse there return false,
        else:
            try: 
                content = container
                for level in path:
                    content = content[level]
                return True
            except:
                return False
        # return false otherwise
        return False


    def remove(self, path, index = None):
        """
        Remove file or chunkhandles
        """
        path = self.process_path(path)
        content = self.files


        # when removing a directory or a file (when index == None)
        if index == None:
            # remove a directory
            if(path[-1] == ""):
                # traverse to the parent directory
                for level in path[:-2]:
                    content = content[level]

                curr_directory_name = path[-2]                
                # access everything under the directory
                for data_name, data_value in list(content[curr_directory_name].items()):
                    # if it's a file
                    if type(data_value) == list and len(data_value) > 0:
                        for chunk in data_value:
                            del self.chunkhandle_map[chunk]

                    # if it'd a directory call this 
                    if type(data_value) == dict and len(data_value) > 0:
                        sub_directory_path = path[:-1] + [data_name] + [""]
                        self.remove(sub_directory_path)
                # delete the directory
                del content[path[-2]]
                
            # remove a file and remove all chunk in the chunkhandle_map according to the chunkhandle
            else:
                file_name = path[-1]
                # traverse to the parent directory of the file
                for level in path[:-1]:
                    content = content[level]

                # access the file remove every chunk info in chunkhandle_map for the file
                for chunk in content[file_name]:
                    del self.chunkhandle_map[chunk]
                
                # now remove the file in metadata beautifully
                del content[path[-1]]

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
    f.make_path("/fun/")
    f.make_path("/fun/cs/")
    f.make_path("/fun/cs/sss/")
    f.make_path("/fun/cs/sss/goku.txt")
    f.make_path("/fun/cs/test.txt")
    f.make_path("/hello.txt")
    f.add("/hello.txt", -1, "1", [1,2,3])
    f.add("/hello.txt", 0, "2", [1,2,3])
    f.add("/fun/cs/test.txt", 1, "3", [1,2,3])
    f.add("/fun/cs/test.txt", 2, "4", [1,2,3])
    f.add("/fun/cs/sss/goku.txt", 3, "5", [1,2,3])


    print("chunkhandle map: ", f.chunkhandle_map)
    print("metadata: ", f.files)
    # print(f.chunkhandle_map)
    print("\n")


    f.remove("/hello.txt")
    print("after remove")
    print("chunkhandle map: ", f.chunkhandle_map)
    print("metadata: ", f.files)
    print("\n")

    f.remove("/fun/")
    print("after remove")
    print("chunkhandle map: ", f.chunkhandle_map)
    print("metadata: ", f.files)
    print("\n")

    """

    print("before: {0}".format(f.files))

    f.make_path("/fun.txt")
    f.add("/fun.txt", -1,"oops",["a"])
    # print("chunk info: {0}".format(chunk_handle))

    print("after: {0}".format(f.files))
    # print(f.chunkhandle_map)
    print("\n")
    # f.retrieve("/fun.txt", 0)




    # print(f.verify_path("/fun.txt"))
    
    f.make_path("/school/")
    print(f.files)
    print(f.chunkhandle_map)
    print("\n")
    # def add(self, path, index, chunkhandle, replicas = None, container = None):
    f.make_path("/school/hello.txt")

    print(f.verify_path("/school/"))


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
    """
