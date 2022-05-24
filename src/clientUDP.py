from socket import *

class ClientUDP:
    def __init__(self):
        self.socket = socket(AF_INET, SOCK_DGRAM)
    
    def startClient(self):
        self.socket.bind(("localhost", 0))
    
    def receiveFrom(self):
        # returns segment, clientAddress 
        return self.socket.recvfrom(2048)

    def sendTo(self, message, clientAddress):
        self.socket.sendto(message, clientAddress)
    
    def shutdown(self):
        # define protocol
        pass
