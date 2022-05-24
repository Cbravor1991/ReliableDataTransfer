from fileinput import filename
from serverUDP import ServerUDP
from protocol import Protocol

UPLOAD = 1
DOWNLOAD = 2
RECPACKAGE = 3

def main():
    server = ServerUDP()
    server.startServer()
    protocol = Protocol()

    while True:

        fileDownload = ""

        segment = protocol.receive(server)
        command = segment[0]

        if command == UPLOAD:
            fileSize, fileName = protocol.processUploadSegment(segment)
            print('Upload {}'.format(command))
            print('size {}'.format(fileSize))
            print('name {}'.format(fileName))
        elif command == DOWNLOAD:
            fileName = protocol.processDownloadSegment(segment)
            print('fileName: {}'.format(fileName))
            # Read file, chunk file and send data to client
        elif command == RECPACKAGE:
            dataSize, data = protocol.processRecPackageSegment(segment)
            print('dataSize {}'.format(dataSize))
            print('data {}'.format(data))
            #concatenar data con fileDownload para formar el file
            if(len(fileDownload) == fileSize):
                print('file {}'.format(fileDownload))





main()