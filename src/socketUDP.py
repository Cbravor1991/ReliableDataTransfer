from socket import *

class SocketUDP:
    def __init__(self) -> None:
        self.socket = socket(AF_INET, SOCK_DGRAM)
    
    def bindSocket(self, host, port):
        self.socket.bind((host, port))
    
    def receiveFrom(self, bytesToReceive):
        # returns segment, clientAddress 
        return self.socket.recvfrom(bytesToReceive)

    def sendTo(self, message, clientAddress):
        self.socket.sendTo(message, clientAddress)
    
    def shutdown(self):
        pass

