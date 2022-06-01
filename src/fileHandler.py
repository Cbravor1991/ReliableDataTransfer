import os.path
from os import path

class FileHandler:

    def getSizeFile (self, path):
        return os.path.getsize(path)

    def openFile(self, path):
        file = open(path, 'rb')
        return file
    
    def closeFile(self, file):
        file.close()

    

    def readFileBytes(self, pos, file, bytesToRead):
        file.seek(pos)
        contents = file.read(bytesToRead)
        return contents

