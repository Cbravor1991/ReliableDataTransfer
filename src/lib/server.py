import threading
import logging

from lib.socketUDP import SocketUDP
from lib.protocol import Protocol
from lib.decoder import Decoder


class Server:
    def __init__(self, addr, port):
        self.connections = dict()
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


    def handleDownload(self, segment):
        fileName = self.protocol.processDownloadSegment(segment)
        print('command {} fileName {}'.format(segment[0], fileName))

        while True: # hasta terminar el download o que haya algun error
            segment, clientAddr = self.protocol.receive(self.serverSocket)
            if Decoder.isACK(segment):
                pass

    def shutdown(self):
        self.serverSocket.shutdown()
            
