from socketUDP import SocketUDP
from protocol import Protocol

UPLOAD = 1
DOWNLOAD = 2
RECPACKAGE = 3

def main():
    serverSocket = SocketUDP()
    serverSocket.bindSocket("localhost", 12000)
    protocol = Protocol()

    while True:

        fileDownload = ""

        segment = protocol.receive(serverSocket)
        command = segment[0]

        if command == UPLOAD:
            fileSize, fileName = protocol.processUploadSegment(segment)
            print('command {} fileSize {} fileName {}'.format(command, fileSize, fileName))
        elif command == DOWNLOAD:
            fileName = protocol.processDownloadSegment(segment)
            print('command {} fileName {}'.format(command, fileName))
        elif command == RECPACKAGE:
            dataSize, data = protocol.processRecPackageSegment(segment)
            if(len(fileDownload) == fileSize):
                print('file {}'.format(fileDownload))
main()