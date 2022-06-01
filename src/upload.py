from client import Client
from fileHandler import FileHandler

def main():
    fileName = 'name'
    path = './texto.txt'
    fileSize = FileHandler.getFileSize(path) 
    file = FileHandler.openFile(path)

    serverAddr = ('localhost', 12000)
    client = Client('localhost', 0)
    try:
        client.upload(fileName, file, fileSize, serverAddr)
    except KeyboardInterrupt:
        print("Shutting down client...")
        client.shutdown()
        print("Client shut down")
    except Exception as e:
        print(e)

    FileHandler.closeFile(file)

main()