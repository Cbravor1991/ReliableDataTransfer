import threading
import logging
from math import ceil
from socket import timeout
from queue import Queue

from lib.selectiveRepeat import SelectiveRepeat
from lib.socketUDP import SocketUDP
from lib.protocol import Protocol
from lib.decoder import Decoder
from lib.encoder import Encoder
from lib.fileHandler import FileHandler

class Server:
    def __init__(self, addr, port, dstPath, transferMethod):
        self.dstPath = dstPath
        self.serverSocket = SocketUDP()
        self.serverSocket.bindSocket(addr, port)
        self.protocol = Protocol()
        self.transferMethod = transferMethod
        self.sendQueue = Queue()
        self.connections = {}

    def start(self):
        # falta borrar las conexiones del dict
        threading.Thread(target=self.senderThread).start()
        while True:
            segment, clientAddr = self.protocol.receive(self.serverSocket)

            if clientAddr in self.connections:
                self.connections[clientAddr].put(segment)
            
            else:
                logging.info(f"New client: {clientAddr}")
                recvQueue = Queue()
                recvQueue.put(segment)
                self.connections[clientAddr] = recvQueue
                if Decoder.isUpload(segment):
                    threading.Thread(target=self.transferMethod.serverUpload, args=(recvQueue, self.sendQueue, clientAddr, self.dstPath)).start()
                elif Decoder.isDownload(segment):
                    threading.Thread(target=self.transferMethod.serverDownload, args=(recvQueue, self.sendQueue, clientAddr, self.dstPath)).start()
            
    def senderThread(self):
        while True:
            segment, clientAddr = self.sendQueue.get()
            if Decoder.isTerminate(segment):
                return
            self.protocol.sendMessage(self.serverSocket, clientAddr, segment)

    def shutdown(self):
        # encolar en todas las conexiones abiertas y en el sendQueue un mensaje de finalizacion, y cerrar el socket
        terminateMsg = Encoder.createTerminateMessage()
        for connection in self.connections:
            self.connections[connection].put(terminateMsg)
        self.sendQueue.put((terminateMsg, None))
        self.serverSocket.shutdown()
            
