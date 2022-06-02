import threading
import logging
from socket import timeout

from lib.socketUDP import SocketUDP
from lib.protocol import Protocol
from lib.decoder import Decoder
from lib.fileHandler import FileHandler

class Server:
    def __init__(self, addr, port, dstPath):
        self.connections = dict()
        self.dstPath = dstPath
        self.serverSocket = SocketUDP()
        self.serverSocket.bindSocket(addr, port)
        self.protocol = Protocol()


    def start(self):
        while True:
            segment, clientAddr = self.protocol.receive(self.serverSocket)
            if Decoder.isUpload(segment):
                self.handleUpload(segment, clientAddr)
            elif Decoder.isDownload(segment):
                self.handleDownload(segment, clientAddr)


    def handleUpload(self, segment, clientAddr):
        fileSize, fileName = self.protocol.processUploadSegment(segment)
        
        ACKMessage = self.protocol.createACKMessage(0)
        self.protocol.sendMessage(self.serverSocket, clientAddr, ACKMessage)
        print('command {} fileSize {} fileName {}'.format(segment[0], fileSize, fileName))
        
        fileDownload = []
        prevSequenceNumber = 0
        while len(fileDownload) != fileSize: # hasta terminar el upload o que haya algun error

            segment, clientAddr = self.protocol.receive(self.serverSocket)
            if Decoder.isRecPackage(segment):            
                sequenceNumber, data = self.protocol.processRecPackageSegment(segment)
                print('Sequence number {}'.format(sequenceNumber))

                ACKMessage = self.protocol.createACKMessage(sequenceNumber)
                self.protocol.sendMessage(self.serverSocket, clientAddr, ACKMessage)

                if sequenceNumber > prevSequenceNumber:
                    fileDownload += data
                prevSequenceNumber = sequenceNumber

        print('file {}'.format(fileDownload))               


    def sendAndReceiveACK(self, msg, clientAddr):
        while True:
            self.protocol.sendMessage(self.serverSocket, clientAddr, msg)
            try:
                segment, _ = self.protocol.receive(self.serverSocket)
                sequenceNumber = self.protocol.processACKSegment(segment)
                print('ACK {}'.format(sequenceNumber))
                break
            except timeout:
                self.serverSocket.addTimeOut()
                print("timeout") 
        return sequenceNumber


    def handleDownload(self, segment, clientAddr):
        MSS = 6

        fileName = self.protocol.processDownloadSegment(segment)
        print('command {} fileName {}'.format(segment[0], fileName))
        path = self.dstPath + fileName
        file = FileHandler.openFile(path)
        fileSize = FileHandler.getFileSize(path)

        sequenceNumber = 0
        sent = 0
        morePackages = True
        while sent < fileSize:
            data = FileHandler.readFileBytes(sent, file, MSS)
            sent += min(len(data), MSS)
            morePackages = len(data) == MSS
            packageMessage = self.protocol.createDownloadPackageMessage(data, sequenceNumber+1, morePackages)
            sequenceNumber = self.sendAndReceiveACK(packageMessage, clientAddr)

        print("File transfer finished")
        FileHandler.closeFile(file)


    def shutdown(self):
        self.serverSocket.shutdown()
            
