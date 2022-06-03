import math
from threading import Timer
from time import sleep
from lib.protocol import Protocol
import threading
from lib.fileHandler import FileHandler
import logging


class SenderForServer:
    def __init__(self, recvQueue, sendQueue, clientAddr, file, fileSize):
        self.window_size = 3
        self.window_start = 0
        self.file = file
        self.file_size = fileSize
        self.file_transfered = 0
        self.currSeqNum = 0
        self.lock = threading.Lock()
        self.MSS = 5
        self.messagesBuffer = [False for i in range(math.ceil(self.file_size/self.MSS))]
        self.timers = [False for i in range(math.ceil(self.file_size/self.MSS))]
        self.protocol = Protocol()
        self.recvQueue = recvQueue
        self.sendQueue = sendQueue
        self.clientAddr = clientAddr
        self.timeToTimeout = 2
        self.rec_thread = threading.Thread(target=self.receivePack)
        self.send_thread = threading.Thread(target=self.sendPack)


    def callFromTimeout(self, index):
        if (self.messagesBuffer[index] is not False):
           
            if (index < self.window_start or self.messagesBuffer[index] == "buffered"):
                self.stop_timer(index)
            else:
                #logging.warning("Timeout")
                print("TIMEOUT del seq {}".format(index))
                #logging.debug("Timeout paquete nro seq {}".format(index))
                #logging.info("Reenviando paquete nro seq {}".format(index))
                self.sendQueue.put((self.messagesBuffer[index], self.clientAddr))

                self.start_timer(index)

    def removeMessage(self, index):
        self.lock.acquire(blocking=True)
        #logging.debug("Removiendo mensaje {}".format(index))
        self.messagesBuffer[index] = False
        self.lock.release()

    def start_timer(self, index):
        self.lock.acquire(blocking=True)
        logging.debug("Iniciando Timer de mensaje {} con un tiempo de {}"
                      .format(index, self.timeToTimeout))
        #logging.info("Iniciando timer de {}".format(index))
        self.timers[index] = Timer(self.timeToTimeout,
                                   self.callFromTimeout,
                                   args=(index,))
        self.timers[index].start()
        self.lock.release()

    def stop_timer(self, index):
        self.lock.acquire(blocking=True)
        if (not self.timers[index]):
            #logging.debug("No habia timer en {}".format(index)
            # )
            pass
        elif(self.timers[index].is_alive()):
            self.timers[index].cancel()
            #logging.debug("Deteniendo timer {}".format(index))
        self.timers[index] = False
        self.lock.release()

    def receivePack(self):
        while self.window_start < math.ceil(self.file_size/self.MSS):
            print("Window start: {}".format(self.window_start))
            try:
                segment = self.recvQueue.get()
            except TimeoutError:
                pass
            sequenceNumber = self.protocol.processACKSegment(segment)
            #   logging.info("Recibiendo paquete ACK {}".format(sequenceNumber))
            print("Recibiendo paquete ACK {}".format(sequenceNumber))
            if (sequenceNumber == self.window_start):
                #logging.debug("El paquete ACK {} coincide con la base ventana"
                 #             .format(sequenceNumber))
                
                self.stop_timer(sequenceNumber)
                self.removeMessage(sequenceNumber)
                self.window_start += 1
                for i in range(self.window_start,
                               self.getTopOfWindow()):
                    if (self.messagesBuffer[i] == 'buffered'):
                        self.window_start += 1
                    else:
                        #logging.debug("WINDOW START: {}"
                        #             .format(self.window_start))
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

        while self.file_transfered < self.file_size:
            #logging.info("Window: {}".format(self.messagesBuffer[
              #                                self.window_start:
                #                              self.window_start +
                  #                            self.window_size]))
            if(self.isNotFullMessageBuffer(self.currSeqNum)):
                data = self.readFile(self.currSeqNum)
                print("Sending: {} seqNum: {}".format(data, self.currSeqNum))
                recMsg = self.protocol.createRecPackageMessage(data, self.currSeqNum)
                
                self.sendQueue.put((recMsg, self.clientAddr))
                
                self.messagesBuffer[self.currSeqNum] = recMsg
                self.start_timer(self.currSeqNum)
                #logging.info('Se envia paquete con nro seq: {}'
                 #             .format(self.currSeqNum))
                self.currSeqNum += 1
                self.file_transfered += len(data)
            else:
                #logging.warning("La ventana se encuentra llena")
                sleep(0.1)

  

    def startServer(self):




        self.send_thread.start()
        self.rec_thread.start()

        self.rec_thread.join()
        self.send_thread.join()
    
    
