import threading
import logging
from math import ceil
from socket import timeout
from lib.selectiveRepeat import SelectiveRepeat
from lib.socketUDP import SocketUDP
from lib.protocol import Protocol
from lib.decoder import Decoder
from lib.fileHandler import FileHandler

class Server:
    def __init__(self, addr, port, dstPath, transferMethod):
        self.connections = dict()
        self.dstPath = dstPath
        self.serverSocket = SocketUDP()
        self.serverSocket.bindSocket(addr, port)
        self.protocol = Protocol()
        self.transferMethod = transferMethod

        


    def stopAndWait(self):
        print("Stop and wait")
        while True:
            segment, clientAddr = self.protocol.receive(self.serverSocket)
            if Decoder.isUpload(segment):
                self.handleUpload(segment, clientAddr)
            elif Decoder.isDownload(segment):
                self.handleDownload(segment, clientAddr)


    def selectiveRepeat(self):
        while True:
            segment, clientAddr = self.protocol.receive(self.serverSocket)
            if Decoder.isUpload(segment):
                self.transferMethod.receiveFileFromClient(segment, clientAddr)
            elif Decoder.isDownload(segment):
                self.transferMethod.sender.startServer(segment)





    def handleUpload(self, segment, clientAddr):
        fileSize, fileName = self.protocol.processUploadSegment(segment)
        file = FileHandler.newFile(self.dstPath, fileName)
        
        ACKMessage = self.protocol.createACKMessage(0)
        self.protocol.sendMessage(self.serverSocket, clientAddr, ACKMessage)
        print('command {} fileSize {} fileName {}'.format(segment[0], fileSize, fileName))
        
        transferred = 0
        prevSequenceNumber = 0
        while transferred != fileSize: # hasta terminar el upload o que haya algun error

            self.serverSocket.setTimeOut(15)
            segment, clientAddr = self.protocol.receive(self.serverSocket)
            if Decoder.isRecPackage(segment):            
                sequenceNumber, data = self.protocol.processRecPackageSegment(segment)
                print('Sequence number {}'.format(sequenceNumber))

                ACKMessage = self.protocol.createACKMessage(sequenceNumber)
                self.protocol.sendMessage(self.serverSocket, clientAddr, ACKMessage)

                if sequenceNumber > prevSequenceNumber:
                    transferred += len(data)
                    file.write(data)
                prevSequenceNumber = sequenceNumber
            elif Decoder.isUpload(segment):
                self.protocol.sendMessage(self.serverSocket, clientAddr, ACKMessage)

        FileHandler.closeFile(file)
        print('Upload finished')               


    def sendAndReceiveACK(self, msg, clientAddr):
        while True:
            try:
                self.serverSocket.setTimeOut(1)
                self.protocol.sendMessage(self.serverSocket, clientAddr, msg)
                segment, _ = self.protocol.receive(self.serverSocket)
                sequenceNumber = self.protocol.processACKSegment(segment)
                print('server recibe ACK {}'.format(sequenceNumber))
                break
            except timeout:
                self.serverSocket.addTimeOut()
                print("timeout, server no recibe el ack. Se reenvia el paquete") 
        return sequenceNumber




    def handleDownload(self, segment, clientAddr):
        MSS = 6

        fileName = self.protocol.processDownloadSegment(segment)


        print('command {} fileName {}'.format(segment[0], fileName))
        path = self.dstPath + fileName
        try:
            file = FileHandler.openFile(path)
            fileSize = FileHandler.getFileSize(path)
        except:
            print('File not found')
            return

        numPackages = ceil(fileSize / MSS)
        sequenceNumber = 0
        sent = 0
        morePackages = True
        while sent < fileSize:
            data = FileHandler.readFileBytes(sent, file, MSS)
            sent += min(len(data), MSS)
            morePackages = numPackages > 1
            packageMessage = self.protocol.createDownloadPackageMessage(data, sequenceNumber+1, morePackages)
            print('server envia el paquete {}'.format(sequenceNumber+1))
            sequenceNumber = self.sendAndReceiveACK(packageMessage, clientAddr)
            numPackages -= 1

        FileHandler.closeFile(file)
        print("Download finished")


    def shutdown(self):
        self.serverSocket.shutdown()
            
