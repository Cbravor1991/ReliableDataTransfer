import os.path
from os import path

class FileHandler:
    def getFileSize (path):
        return os.path.getsize(path)

    def openFile(path):
        file = open(path, 'rb')
        return file
        
    def closeFile(file):
        file.close()

    def readFileBytes(pos, file, bytesToRead):
        file.seek(pos)
        contents = file.read(bytesToRead)
        return contents

