from fileinput import filename
from socketUDP import SocketUDP
from protocol import Protocol

UPLOAD = 1
DOWNLOAD = 2
RECDATA = 3

def main():
    serverSocket = SocketUDP()
    serverSocket.bindSocket("localhost", 12000)
    protocol = Protocol()

    while True:

        segment = protocol.receive(serverSocket)
        command = segment[0]
        if command == UPLOAD:
            fileSize, fileName = protocol.processUploadSegment(segment)
        elif command == DOWNLOAD:
            fileName = protocol.processDownloadSegment(segment)
        elif command == RECDATA:
            pass
main()