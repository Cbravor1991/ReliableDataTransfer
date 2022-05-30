import os.path
from os import path

class FileHandler:

    def getSizeFile (self, path):
        return os.path.getsize(path)
    

    

    def readFileBytes(self, filepath, bytesToRead):
        file = open(filepath, 'rb')
        filePosition = file.tell()
        if (filePosition < self.getSizeFile(self, filepath)):
            rest= filePosition- bytesToRead
            print (rest)
            if (rest< bytesToRead):
                contents = file.read(1)
            else:
                contents = file.read(bytesToRead)

        return contents


def main(self):

    file_name = 'name'
    path = './texto.txt'
    file_size = self.getSizeFile(self, path)  
    contenido = self.readFileBytes(self, path, 5)


    print(file_size)
    print (contenido)

main(FileHandler)
    
