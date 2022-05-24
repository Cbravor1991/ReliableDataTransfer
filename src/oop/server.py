from sqlalchemy import case
from serverUDP import ServerUDP
from protocol import Protocol

UPLOAD = 1
DOWNLOAD = 2

def main():
    server = ServerUDP()
    server.startServer()
    protocol = Protocol()

    while True:
        command, clientAddress = protocol.receiveCommandFromClient(server)
        if command == UPLOAD:
            
            print("upload")
        elif command == DOWNLOAD:
            print("download")
        

main()