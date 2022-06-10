import math
from socket import timeout
from threading import Timer
from time import sleep
from lib.socketUDP import SocketUDP
from lib.protocol import Protocol
import threading
from lib.fileHandler import FileHandler
import logging


class Sender:
    def __init__(self, file, serverPort, fileSize):
        self.window_size = 200
        self.window_start = 0
        self.file = file
        self.file_size = fileSize
        self.file_transfered = 0
        self.currSeqNum = 0
        self.lock = threading.Lock()
        self.MSS = 1000
        self.messagesBuffer = [False for i in range(math.ceil(self.file_size/self.MSS))]
        self.timers = [False for i in range(math.ceil(self.file_size/self.MSS))]
        self.socket = SocketUDP()
        self.protocol = Protocol()
        self.serverAddress = ("localhost", serverPort)
        self.timeToTimeout = 2
        self.rec_thread = threading.Thread(target=self.receivePack)
        self.send_thread = threading.Thread(target=self.sendPack)
        self.active = True


    def callFromTimeout(self, index):
        if not self.active:
            return
        if (self.messagesBuffer[index] is not False):
           
            if (index < self.window_start or self.messagesBuffer[index] == "buffered"):
                self.stop_timer(index)
            else:
                logging.debug("TIMEOUT del seq {}".format(index))
                self.protocol.sendMessage(self.socket,
                                        self.serverAddress,
                                        self.messagesBuffer[index])
                self.start_timer(index)

    def removeMessage(self, index):
        self.lock.acquire(blocking=True)
        self.messagesBuffer[index] = False
        self.lock.release()

    def start_timer(self, index):
        self.lock.acquire(blocking=True)
        logging.debug("Iniciando Timer de mensaje {} con un tiempo de {}"
                      .format(index, self.timeToTimeout))
        self.timers[index] = Timer(self.timeToTimeout,
                                   self.callFromTimeout,
                                   args=(index,))
        self.timers[index].start()
        self.lock.release()

    def stop_timer(self, index):
        self.lock.acquire(blocking=True)
        if (not self.timers[index]):
            pass
        elif(self.timers[index].is_alive()):
            self.timers[index].cancel()
        self.timers[index] = False
        self.lock.release()

    def receivePack(self):
        while self.window_start < math.ceil(self.file_size/self.MSS) and self.active:
            logging.debug("Window start: {}".format(self.window_start))
            try:
                segment, serverAddress = self.protocol.receive(self.socket)
            except:
                continue

            sequenceNumber = self.protocol.processACKSegment(segment)
            logging.debug("Recibido ACK {}".format(sequenceNumber))
            if (sequenceNumber == self.window_start):
                self.stop_timer(sequenceNumber)
                self.removeMessage(sequenceNumber)
                self.window_start += 1
                for i in range(self.window_start,
                               self.getTopOfWindow()):
                    if (self.messagesBuffer[i] == 'buffered'):
                        self.window_start += 1
                    else:
                        break
                
            elif (sequenceNumber > self.window_start and
                  sequenceNumber < self.window_start + self.window_size):
                self.stop_timer(sequenceNumber)
                self.removeMessage(sequenceNumber)
                self.messagesBuffer[sequenceNumber] = 'buffered'

    def readFile(self, index):
        return FileHandler.readFileBytes(index * self.MSS, self.file, self.MSS)

    def getTopOfWindow(self):
        window_top = self.window_start + self.window_size
        file_top = math.ceil(self.file_size/self.MSS)
        if (window_top > file_top):
            return file_top
        else:
            return window_top

    def isNotFullMessageBuffer(self, seqNumber):
        total_messages = 0
        for i in range(self.window_start,
                       self.getTopOfWindow()):
            if (self.messagesBuffer[i] is not False):
                total_messages += 1
        seqNumberBelowWindow = seqNumber < self.window_start + self.window_size
        return total_messages <= self.window_size and seqNumberBelowWindow

    def sendPack(self):
        while self.file_transfered < self.file_size and self.active:
            if(self.isNotFullMessageBuffer(self.currSeqNum)):
                data = self.readFile(self.currSeqNum)
                logging.debug("Enviando parquete: {}".format(self.currSeqNum))
                recMsg = self.protocol.createRecPackageMessage(data,
                                                               self.currSeqNum)
                
                self.protocol.sendMessage(self.socket,
                                          self.serverAddress,
                                          recMsg)
                
                self.messagesBuffer[self.currSeqNum] = recMsg
                self.start_timer(self.currSeqNum)
                self.currSeqNum += 1
                self.file_transfered += len(data)
            else:
                sleep(0.1)

    def startClienUpload(self, clientSocket, filename, file, fileSize, serverAddr):
        uploadMsg = self.protocol.createUploadMessage(fileSize, filename)
        self.file = file
        self.file_size = fileSize
        self.socket = clientSocket

        while True:
            try:
                self.socket.setTimeOut(1)
                self.protocol.sendMessage(clientSocket, serverAddr, uploadMsg)
                segment, serverAddr = self.protocol.receive(clientSocket)
                sequenceNumber = self.protocol.processACKSegment(segment)
                break
            except timeout:
                logging.debug("Timeout")

        self.messagesBuffer = [False for i in range(math.ceil(self.file_size/self.MSS))]
        self.timers = [False for i in range(math.ceil(self.file_size/self.MSS))]
        
        self.send_thread.start()
        self.rec_thread.start()

        self.rec_thread.join()
        self.send_thread.join()

    def startServer(self, segment, serverSocket, clientAddr):

        self.socket = serverSocket
        self.serverAddress = clientAddr

        self.messagesBuffer = [False for i in range(math.ceil(self.file_size/self.MSS))]
        self.timers = [False for i in range(math.ceil(self.file_size/self.MSS))]

        self.send_thread.start()
        self.rec_thread.start()
    
    
