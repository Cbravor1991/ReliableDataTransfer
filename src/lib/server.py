import threading
import logging
from math import ceil
from socket import timeout
from queue import Queue

from lib.selectiveRepeat import SelectiveRepeat
from lib.socketUDP import SocketUDP
from lib.protocol import Protocol
from lib.decoder import Decoder
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
        while True:
            segment, clientAddr = self.protocol.receive(self.serverSocket)

            if clientAddr in self.connections:
                self.connections[clientAddr].put(segment)
            
            else:
                print(f"Cliente nuevo: {clientAddr}")
                recvQueue = Queue()
                recvQueue.put(segment)
                self.connections[clientAddr] = recvQueue
                if Decoder.isUpload(segment):
                    threading.Thread(target=self.transferMethod.serverUpload, args=(recvQueue, self.sendQueue, clientAddr, self.dstPath)).start()
                elif Decoder.isDownload(segment):
                    threading.Thread(target=self.transferMethod.serverDownload, args=(recvQueue, self.sendQueue, clientAddr, self.dstPath)).start()
            
            segment, clientAddr = self.sendQueue.get()
            if segment:
                self.protocol.sendMessage(self.serverSocket, clientAddr, segment)

    def shutdown(self):
        self.serverSocket.shutdown()
            
