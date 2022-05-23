from curses import resize_term
from itertools import count
from socket import *
        
class RDTserver:
    def __init__(self, segment):
        self.originPort = segment[:2]
        self.destinationPort  = segment[2:4] 
        self.length = segment[4:6]
        self.checksum  = segment[6:8]
        self.data = segment[8:]

        print(self.originPort) # veo que recibo
        print(self.destinationPort)
        print(self.length)
        print(self.checksum)
        print(self.data)

    def demultiplex(self):
        return self.data

    def segmentOk(self):
        print(self.originPort.decode() + self.destinationPort.decode() + self.length.decode())
        print(self.checksum)
        res = self.originPort.decode() + self.destinationPort.decode() + self.length.decode() + self.checksum.decode()
        return res==-1



def mainServer():
    serverPort = 12000
    serverSocket = socket(AF_INET, SOCK_DGRAM)
    serverSocket.bind(('', serverPort))

    while True:
        segment, clientAddress = serverSocket.recvfrom(2048)
        print(segment)
        rdtServer = RDTserver(segment)

        if not rdtServer.segmentOk():
            print("Error checkSum")
            exit()

        message = len(rdtServer.demultiplex())
        modifiedMessage = "La cantidad de caracteres que tiene el numero es " + len(message)
        serverSocket.sendto(modifiedMessage.encode(), clientAddress)

mainServer()