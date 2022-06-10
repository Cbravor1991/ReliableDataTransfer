from fileinput import filename
import threading
import logging
from socket import timeout
from time import sleep

from lib.socketUDP import SocketUDP
from lib.protocol import Protocol
from lib.fileHandler import FileHandler
from lib.receiver import Receiver
from lib.sender import Sender


MSS = 6


class Client:
    def __init__(self, addr, port, transferMethod):
        self.clientSocket = SocketUDP()
        self.clientSocket.bindSocket(addr, port)
        self.transferMethod = transferMethod

    def upload(self, filename, file, fileSize, serverAddr):
        self.transferMethod.clientUpload(self.clientSocket, filename, file, fileSize, serverAddr)

    def download(self, fileName, path, serverAddr):
        self.transferMethod.clientDownload(self.clientSocket, fileName, path, serverAddr)
              
    def shutdown(self):
        self.transferMethod.sender.active = False
        sleep(1)
        self.clientSocket.shutdown()
            
