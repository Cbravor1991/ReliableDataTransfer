import logging
from lib.decoder import Decoder
from lib.encoder import Encoder
from lib.protocol import Protocol
from lib.receiver import Receiver
from lib.sender import Sender
from lib.fileHandler import FileHandler
import math
from lib.senderForServer import SenderForServer
from lib.stopAndWait import StopAndWait, FINAL_ACK_TRIES
from socket import timeout

MSS = 1000
window_size = 200
window_start = 0

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
        self.sender = Sender(file, serverAddr[1], fileSize)
        self.sender.startClienUpload(clientSocket, filename, file, fileSize, serverAddr)

    def clientDownload(self, clientSocket, fileName, path, serverAddr):
        
        MSS = 1000
        window_size = 200
        window_start = 0

        downloadMsg = self.protocol.createDownloadMessage(fileName)
        stopAndWait = StopAndWait()
        try:
            segment = stopAndWait.socketSendAndReceiveFileSize(downloadMsg, serverAddr, clientSocket)
        except:
            logging.warning('Timeouts exceeded.')
            return

        fileSize = Decoder.processFileSize(segment)
        
        ackFSMsg = self.protocol.createACKMessage(0)
        self.protocol.sendMessage(clientSocket, serverAddr, ackFSMsg)

        

        segmentsToReceive = math.ceil(fileSize/MSS)
        messagesBuffer = [False for i in range(segmentsToReceive)]


        seqNum = 0
        file = FileHandler.newFile(path, fileName)
        logging.debug(fileSize)
        while window_start < segmentsToReceive:
            try:
                segment, serverAddr  = self.protocol.receive(clientSocket)
            except timeout:
                continue
            if (Decoder.isRecPackage(segment)):
                seqNum, data = self.protocol.processRecPackageSegment(segment)
                if (self.isInsideWindow(window_start, window_size, seqNum)):
                    ACKMessage = self.protocol.createACKMessage(seqNum)
                    logging.debug("Se envio ACK: {}".format(seqNum))
                    self.protocol.sendMessage(clientSocket, serverAddr, ACKMessage)
                    
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
                elif (self.isBelowWindow(seqNum, window_start)):
                    logging.debug("Below window")
                    ACKMessage = self.protocol.createACKMessage(seqNum)
                    self.protocol.sendMessage(clientSocket, serverAddr, ACKMessage)
            elif (Decoder.isDownload(segment)):
                logging.debug("Es download")
                self.protocol.sendMessage(clientSocket, serverAddr, ACKMessage)
            elif (Decoder.isFileSize(segment)):
                self.protocol.sendMessage(clientSocket, serverAddr, ackFSMsg)

        ACKMessage = self.protocol.createACKMessage(seqNum)
        for _ in range(FINAL_ACK_TRIES):
            self.protocol.sendMessage(clientSocket, serverAddr, ACKMessage)

        file.close()


    def serverDownload(self, recvQueue, sendQueue, clientAddr, dstPath):

        segment = recvQueue.get()
        fileName = self.protocol.processDownloadSegment(segment)

        logging.debug('command {} fileName {}'.format(segment[0], fileName))
        path = dstPath + fileName

        try:
            file = FileHandler.openFile(path)
            fileSize = FileHandler.getFileSize(path)
        except:
            logging.debug(f'Download from {clientAddr}: File not found')
            return

        fileSizeSegment = Encoder.createFileSize(fileSize)

        stopAndWait = StopAndWait()
        seqNum = stopAndWait.sendAndReceiveACK(fileSizeSegment,clientAddr, recvQueue, sendQueue)

        sender = SenderForServer(recvQueue, sendQueue, clientAddr, file, fileSize)
        sender.startServer()

        if sender.finished:
            logging.info(f'Download from {clientAddr}: File {fileName} finished')
   


    def serverUpload(self,recvQueue, sendQueue, clientAddr, dstPath):
        window_size = 200
        window_start = 0
        
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
                elif (self.isBelowWindow(seqNum, window_start)):
                    ACKMessage = self.protocol.createACKMessage(seqNum)
                    sendQueue.put((ACKMessage, clientAddr))
            elif (Decoder.isUpload(segment)):
                sendQueue.put((ACKMessage, clientAddr))
            elif (Decoder.isTerminate(segment)):
                logging.debug(f'Closed server: ending thread {clientAddr}...')
                return

        ACKMessage = self.protocol.createACKMessage(seqNum)
        for _ in range(FINAL_ACK_TRIES):
            sendQueue.put((ACKMessage, clientAddr))

        logging.info(f'Upload from {clientAddr}: File {fileName} finished')
        file.close()

    
    