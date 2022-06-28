import math
from threading import Timer
from time import sleep
from lib.protocol import Protocol
from lib.decoder import Decoder
import threading
from lib.fileHandler import FileHandler
import logging


class SenderForServer:
    def __init__(self, recvQueue, sendQueue, clientAddr, file, fileSize):
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
        self.protocol = Protocol()
        self.recvQueue = recvQueue
        self.sendQueue = sendQueue
        self.clientAddr = clientAddr
        self.timeToTimeout = 2
        self.rec_thread = threading.Thread(target=self.receivePack)
        self.send_thread = threading.Thread(target=self.sendPack)
        self.lastPackAckedCounter = 0
        self.active = True
        self.finished = False


    def callFromTimeout(self, index):
        if not self.active:
            return
        if (self.messagesBuffer[index] is not False):
            if (index == math.ceil(self.file_size/self.MSS)-1):
                self.lastPackAckedCounter += 1
                logging.debug(self.lastPackAckedCounter)
                if (self.lastPackAckedCounter > 10):
                    self.stop_timer(index)

            if (index < self.window_start or self.messagesBuffer[index] == "buffered"):
                self.stop_timer(index)
            
            else:
                logging.debug("Timeot del paquete numero {}".format(index))
                self.sendQueue.put((self.messagesBuffer[index], self.clientAddr))
                self.start_timer(index)

    def removeMessage(self, index):
        self.lock.acquire(blocking=True)
        self.messagesBuffer[index] = False
        self.lock.release()

    def start_timer(self, index):
        self.lock.acquire(blocking=True)
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
        while self.window_start < math.ceil(self.file_size/self.MSS):
            logging.debug("Window start: {}".format(self.window_start))
            try:
                segment = self.recvQueue.get()
            except TimeoutError:
                continue
            if (Decoder.isTerminate(segment)):
                self.active = False
                return

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
                logging.debug("Enviando paquete de datos {}".format(self.currSeqNum))
                recMsg = self.protocol.createRecPackageMessage(data, self.currSeqNum)
                
                self.sendQueue.put((recMsg, self.clientAddr))
                
                self.messagesBuffer[self.currSeqNum] = recMsg
                self.start_timer(self.currSeqNum)
                self.currSeqNum += 1
                self.file_transfered += len(data)
            else:
                sleep(0.1)
        
        if self.file_transfered >= self.file_size:
            self.finished = True

  

    def startServer(self):


        logging.debug(math.ceil(self.file_size/self.MSS))

        self.send_thread.start()
        self.rec_thread.start()

        self.send_thread.join()
        # self.rec_thread.join()

        


    
    
