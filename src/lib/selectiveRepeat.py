from fileinput import filename
from lib import client
from lib.decoder import Decoder
from lib.encoder import Encoder
from lib.protocol import Protocol
from receiver import Receiver
from sender import Sender
from lib.fileHandler import FileHandler

class SelectiveRepeat:


    def __init__(self) -> None:
        self.protocol = Protocol()
    

    def upload(self, clientSocket, filename, file, fileSize, serverAddr):
        sender = Sender(file, serverAddr[1], fileSize)
        sender.startClient(clientSocket, filename, file, fileSize, serverAddr)

    def download(self, clientSocket, fileName, path, serverAddr):
        receiver = Receiver()
        receiver.receiveFileFromServer( clientSocket, fileName, path, serverAddr)

    def sendFileToClient(self, segment, serverSocket, clientAddr):
        fileName = self.protocol.processDownloadSegment(segment)
        

        print('command {} fileName {}'.format(segment[0], fileName))
        path = './' + fileName
        print(path)
        try:
            file = FileHandler.openFile(path)
        except:
            print('File not found')
            return
        
        fileSize = FileHandler.getFileSize(path)
        fileSizeSegment = Encoder.createFileSize(fileSize)
        self.protocol.sendMessage(serverSocket, clientAddr, fileSizeSegment)

        print("FUILE SIZE: {}".format(fileSize))
        sender = Sender(file, 5, fileSize )
        sender.startServer(segment, serverSocket, clientAddr)
    
    def receiveFileFromClient(self, segment, clientAddr, serverSocket):
        receiver = Receiver()
        receiver.receive(segment, clientAddr, serverSocket)


    
    