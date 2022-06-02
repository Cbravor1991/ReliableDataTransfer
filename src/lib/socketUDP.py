from socket import *

N_TIMEOUTS = 10000

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
        try:
            self.socket.sendto(message, clientAddress)
        except TypeError:
            print("Tried to send a {} message".format(message))
    
    def shutdown(self):
        self.socket.close()
    
    def addTimeOut(self):
        self.tryTimeOuts += 1
        if self.tryTimeOuts >= N_TIMEOUTS:
            raise Exception('Timeouts exceeded')

    def setTimeOut(self, time):
        self.socket.settimeout(time)