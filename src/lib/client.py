from fileinput import filename
import threading
import logging
from socket import timeout

from lib.socketUDP import SocketUDP
from lib.protocol import Protocol
from lib.fileHandler import FileHandler


MSS = 6


class Client:
    def __init__(self, addr, port):
        self.clientSocket = SocketUDP()
        self.clientSocket.bindSocket(addr, port)
        self.protocol = Protocol()


    def sendAndReceiveACK(self, msg, serverAddr):
        while True:
            self.protocol.sendMessage(self.clientSocket, serverAddr, msg)
            try:
                segment, _ = self.protocol.receive(self.clientSocket)
                # que pasa si se recibe un paquete que no es ACK? deberia saltar excepcion en el decoder
                sequenceNumber = self.protocol.processACKSegment(segment)
                print('ACK {}'.format(sequenceNumber))
                break
            except timeout:
                self.clientSocket.addTimeOut()
                print("timeout") 
        return sequenceNumber


    def upload(self, fileName, file, fileSize, serverAddr):
        self.clientSocket.setTimeOut(1) #Que valor poner?

        uploadMessage = self.protocol.createUploadMessage(fileSize, fileName)
        sequenceNumber = self.sendAndReceiveACK(uploadMessage, serverAddr)

        uploaded = 0
        while uploaded < fileSize:
            data = FileHandler.readFileBytes(uploaded, file, MSS)
            print(data, fileSize, uploaded)
            packageMessage = self.protocol.createRecPackageMessage(data, sequenceNumber+1)
            sequenceNumber = self.sendAndReceiveACK(packageMessage, serverAddr)
            print( "len(data) {}".format(len(data)))
            uploaded += min(len(data), MSS)
        print("Upload finished")


    def download(self, fileName, path, serverAddr):
        self.clientSocket.setTimeOut(1) 
        downloadMessage = self.protocol.createDownloadMessage(fileName)
        self.protocol.sendMessage(self.clientSocket, serverAddr, downloadMessage)
        
        downloaded = []
        prevSequenceNumber = 0
        morePackages = True
        while morePackages:

            segment, serverAddr = self.protocol.receive(self.clientSocket)
            sequenceNumber, morePackages, data = self.protocol.processDownloadPackageSegment(segment)
            print('Sequence number {}'.format(sequenceNumber))

            ACKMessage = self.protocol.createACKMessage(sequenceNumber)
            self.protocol.sendMessage(self.clientSocket, serverAddr, ACKMessage)

            if sequenceNumber > prevSequenceNumber:
                downloaded += data
            prevSequenceNumber = sequenceNumber

        print('file {}'.format(downloaded)) 
        
              
    def shutdown(self):
        self.clientSocket.shutdown()
            
