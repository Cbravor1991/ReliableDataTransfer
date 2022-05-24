from socket import *

class ServerUDP:
    def __init__(self) -> None:
        self.socket = socket(AF_INET, SOCK_DGRAM)
    
    def startServer(self):
        self.socket.bind(("localhost", 12000))
    
    def receiveFrom(self, bytesToReceive):
        # returns segment, clientAddress 
        return self.socket.recvfrom(bytesToReceive)

    def sendTo(self, message, clientAddress):
        self.socket.sendTo(message, clientAddress)
    
    def shutdown(self):
        # define protocol
        pass
