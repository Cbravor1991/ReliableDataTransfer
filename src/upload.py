from lib.client import Client
from lib.fileHandler import FileHandler
from lib.arguments import parse_client_upload

def main():
    args = parse_client_upload()
    
    fileSize = FileHandler.getFileSize(args.src) 
    file = FileHandler.openFile(args.src)
    serverAddr = (args.host, args.port)

    client = Client('localhost', 0)
    try:
        client.upload(args.filename, file, fileSize, serverAddr)
    except KeyboardInterrupt:
        print("Shutting down client...")
    except Exception as e:
        print(e)

    FileHandler.closeFile(file)
    client.shutdown()
    print("Client shut down")


main()