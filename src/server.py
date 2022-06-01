import threading
import logging

from socketUDP import SocketUDP
from protocol import Protocol
from decoder import Decoder


class Server:
    def __init__(self, addr, port):
        self.addr = addr
        self.port = port
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
            else:
                raise Exception("Error: corrupt segment")


    def handleUpload(self, segment, clientAddr):
        fileSize, fileName = self.protocol.processUploadSegment(segment)
        ACKMessage = self.protocol.createACKMessage(0)
        self.protocol.sendMessage(self.serverSocket, clientAddr, ACKMessage)
        print('command {} fileSize {} fileName {}'.format(segment[0], fileSize, fileName))
        fileDownload = []
        last_seq = 0
        while True: # hasta terminar el upload o que haya algun error

            segment, clientAddr = self.protocol.receive(self.serverSocket)
            
            if Decoder.isRecPackage(segment):
                sequenceNumber, checkSum, data = self.protocol.processRecPackageSegment(segment)
                # if not (self.protocol.verifyCheckSum(checkSum, data)):
                #     exit()
                print('Sequence number {}'.format(sequenceNumber))

                ACKMessage = self.protocol.createACKMessage(sequenceNumber)
                self.protocol.sendMessage(self.serverSocket, clientAddr, ACKMessage)

                if sequenceNumber > last_seq:
                      fileDownload += data

                if(len(fileDownload) == fileSize):
                    print('file {}'.format(fileDownload))
                    break
                last_seq = sequenceNumber
                    
            


    def handleDownload(self, segment):
        fileName = self.protocol.processDownloadSegment(segment)
        print('command {} fileName {}'.format(segment[0], fileName))

        while True: # hasta terminar el download o que haya algun error
            segment, clientAddr = self.protocol.receive(self.serverSocket)
            if Decoder.isACK(segment):
                pass

    def shutdown(self):
        self.serverSocket.shutdown()
            
