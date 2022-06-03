from fileinput import filename
from lib import client
from lib.decoder import Decoder
from lib.encoder import Encoder
from lib.protocol import Protocol
from receiver import Receiver
from sender import Sender
from lib.fileHandler import FileHandler
import math
class SelectiveRepeat:


    def __init__(self) -> None:
        self.protocol = Protocol()
    

    def getTopOfWindow(self, segmentsToReceive, window_start, window_size):
        window_top = window_start + window_size
        if (window_top > segmentsToReceive):
            return segmentsToReceive
        else:
            return window_top

    def isInsideWindow(self, window_start, window_size, value):
        return (value >= window_start) and (value < window_size + window_start)

    def isBelowWindow(self, seqNum, window_start):
        return seqNum < window_start


    def clientUpload(self, clientSocket, filename, file, fileSize, serverAddr):

        sender = Sender(file, serverAddr[1], fileSize)
        sender.startClienUpload(clientSocket, filename, file, fileSize, serverAddr)

    def clientDownload(self, clientSocket, fileName, path, serverAddr):
        receiver = Receiver()
        receiver.receiveFileFromServer(clientSocket, fileName, path, serverAddr)

    def serverDownload(self, recvQueue, sendQueue, clientAddr, dstPath):

        segment = recvQueue.get()
        fileName = self.protocol.processDownloadSegment(segment)

        print('command {} fileName {}'.format(segment[0], fileName))
        path = dstPath + fileName

        try:
            file = FileHandler.openFile(path)
            fileSize = FileHandler.getFileSize(path)
        except:
            print('File not found')
            return

        fileSizeSegment = Encoder.createFileSize(fileSize)
        sendQueue.put((fileSizeSegment, clientAddr))
        
        #sender = Sender(file, 5, fileSize )
        #sender.startServer(segment, serverSocket, clientAddr)
    


    def serverUpload(self,recvQueue, sendQueue, clientAddr, dstPath):
        window_size = 3
        window_start = 0
        MSS = 5
        
        segment = recvQueue.get()
        fileSize, fileName = self.protocol.processUploadSegment(segment)
        segmentsToReceive = math.ceil(fileSize/MSS)
        messagesBuffer = [False for i in range(segmentsToReceive)]


        ACKMessage = self.protocol.createACKMessage(0)
        sendQueue.put((ACKMessage, clientAddr))
        file = FileHandler.newFile(dstPath, fileName)
        
        while window_start < segmentsToReceive:
            segment = recvQueue.get()
            if (Decoder.isRecPackage(segment)):
                seqNum, data = self.protocol.processRecPackageSegment(segment)
                if (self.isInsideWindow(window_start, window_size, seqNum)):
                    ACKMessage = self.protocol.createACKMessage(seqNum)
                    sendQueue.put((ACKMessage, clientAddr))
                    messagesBuffer[seqNum] = data
                    # verifico buffereados
                    if (seqNum == window_start):
                        file.write(messagesBuffer[seqNum])
                        window_start += 1
                        while window_start < self.getTopOfWindow(segmentsToReceive, window_start, window_size):
                                if (messagesBuffer[window_start] is not False):
                                    file.write(messagesBuffer[window_start])
                                    window_start += 1
                                else:
                                    break
                elif (self.isBelowWindow(self, seqNum, window_start)):
                    ACKMessage = self.protocol.createACKMessage(seqNum)
                    sendQueue.put((ACKMessage, clientAddr))
            elif (Decoder.isUpload(segment)):
                sendQueue.put((ACKMessage, clientAddr))
        file.close()

    
    