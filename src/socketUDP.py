from socket import *

N_TIMEOUTS = 5

class SocketUDP:
    def __init__(self):
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.tryTimeOuts = 0
    
    def bindSocket(self, host, port):
        self.socket.bind((host, port))
    
    def receiveFrom(self, bytesToReceive):
        # returns segment, clientAddress 
        return self.socket.recvfrom(bytesToReceive)

    def sendTo(self, message, clientAddress):
        self.socket.sendto(message, clientAddress)
    
    def shutdown(self):
        self.socket.close()
    
    def addTimeOut(self):
        self.tryTimeOuts += 1
        if self.tryTimeOuts >= N_TIMEOUTS:
            self.shutdown()
            raise Exception('Timeouts exceeded')

    def setTimeOut(self, time):
        self.socket.settimeout(time)