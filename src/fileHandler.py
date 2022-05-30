import os.path
from os import path

class FileHandler:

    def getSizeFile (self, path):
        return os.path.getsize(path)
        

    def readFileBytes(self, filepath, bytesToRead):
        file = open(filepath, 'rb')
        contents = file.read(bytesToRead)
        return contents






    
    
    
