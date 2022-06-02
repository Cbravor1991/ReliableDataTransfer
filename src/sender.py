import math
from socket import socket
from threading import Timer
from time import sleep
from lib.socketUDP import SocketUDP
from lib.protocol import Protocol
import threading
from lib.fileHandler import FileHandler
import logging


class Sender:
    def __init__(self, path, serverPort):
        self.window_size = 200
        self.window_start = 0
        self.file = FileHandler.openFile(path)
        self.file_size = FileHandler.getFileSize(path)
        self.file_transfered = 0
        self.currSeqNum = 0
        self.lock = threading.Lock()
        self.MSS = 200
        self.messagesBuffer = [False for i in range(math.ceil(self.file_size/self.MSS))]
        self.timers = [False for i in range(math.ceil(self.file_size/self.MSS))]
        self.socket = SocketUDP()
        self.protocol = Protocol()
        self.serverAddress = ("localhost", serverPort)
        self.timeToTimeout = 2
        self.rec_thread = threading.Thread(target=self.receivePack)
        self.send_thread = threading.Thread(target=self.sendPack)

    def callFromTimeout(self, index):
        if (self.messagesBuffer[index] is not False):
           
            if (index < self.window_start or self.messagesBuffer[index] == "buffered"):
                self.stop_timer(index)
            else:
                logging.warning("Timeout")
                print("TIMEOUT del seq {}".format(index))
                logging.debug("Timeout paquete nro seq {}".format(index))
                logging.info("Reenviando paquete nro seq {}".format(index))
                self.protocol.sendMessage(self.socket,
                                        self.serverAddress,
                                        self.messagesBuffer[index])
                self.start_timer(index)

    def removeMessage(self, index):
        self.lock.acquire(blocking=True)
        logging.debug("Removiendo mensaje {}".format(index))
        self.messagesBuffer[index] = False
        self.lock.release()

    def start_timer(self, index):
        self.lock.acquire(blocking=True)
        logging.debug("Iniciando Timer de mensaje {} con un tiempo de {}"
                      .format(index, self.timeToTimeout))
        logging.info("Iniciando timer de {}".format(index))
        self.timers[index] = Timer(self.timeToTimeout,
                                   self.callFromTimeout,
                                   args=(index,))
        self.timers[index].start()
        self.lock.release()

    def stop_timer(self, index):
        self.lock.acquire(blocking=True)
        if (not self.timers[index]):
            logging.debug("No habia timer en {}".format(index))
        elif(self.timers[index].is_alive()):
            self.timers[index].cancel()
            logging.debug("Deteniendo timer {}".format(index))
        self.timers[index] = False
        self.lock.release()

    def receivePack(self):
        while self.window_start < math.ceil(self.file_size/self.MSS):
            print("Window start: {}".format(self.window_start))
            segment, serverAddress = self.protocol.receive(self.socket)
            sequenceNumber = self.protocol.processACKSegment(segment)
            logging.info("Recibiendo paquete ACK {}".format(sequenceNumber))
            print("Recibiendo paquete ACK {}".format(sequenceNumber))
            if (sequenceNumber == self.window_start):
                logging.debug("El paquete ACK {} coincide con la base ventana"
                              .format(sequenceNumber))
                
                self.stop_timer(sequenceNumber)
                self.removeMessage(sequenceNumber)
                self.window_start += 1
                for i in range(self.window_start,
                               self.getTopOfWindow()):
                    if (self.messagesBuffer[i] == 'buffered'):
                        self.window_start += 1
                    else:
                        logging.debug("WINDOW START: {}"
                                      .format(self.window_start))
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
            logging.info("Window: {}".format(self.messagesBuffer[
                                             self.window_start:
                                             self.window_start +
                                             self.window_size]))
            if(self.isNotFullMessageBuffer(self.currSeqNum)):
                data = self.readFile(self.currSeqNum)
                recMsg = self.protocol.createRecPackageMessage(data,
                                                               self.currSeqNum)
                self.protocol.sendMessage(self.socket,
                                          self.serverAddress,
                                          recMsg)
                
                self.messagesBuffer[self.currSeqNum] = recMsg
                self.start_timer(self.currSeqNum)
                logging.info('Se envia paquete con nro seq: {}'
                             .format(self.currSeqNum))
                self.currSeqNum += 1
                self.file_transfered += len(data)
            else:
                logging.warning("La ventana se encuentra llena")
                sleep(0.1)

    def start(self):
        self.socket.bindSocket("localhost", 0)
        print(self.file_size)
        uploadMsg = self.protocol.createUploadMessage(self.file_size, "Elnombredelarchivo")
        
        while True:
            self.socket.setTimeOut(1)
            try:
                self.protocol.sendMessage(self.socket, self.serverAddress, uploadMsg)
                segment, clientAddr = self.protocol.receive(self.socket)
                sequenceNumber = self.protocol.processACKSegment(segment)
                break
            except Exception as e:
                print("Timeout {}".format(e))


        self.rec_thread.start()
        self.send_thread.start()

        self.send_thread.join()
        self.rec_thread.join()
    
    
