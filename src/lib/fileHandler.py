import os.path
from os import path

from regex import E

class FileHandler:
    def getFileSize (path):
        return os.path.getsize(path)

    def openFile(path):
        file = open(path, 'rb')
        return file

    def newFile(path, filename):
        if not os.path.exists(path):
            raise Exception("Path does not exist")
        return open(str(path) + str(filename), 'wb')
        
    def closeFile(file):
        file.close()

    def readFileBytes(pos, file, bytesToRead):
        file.seek(pos)
        contents = file.read(bytesToRead)
        return contents

