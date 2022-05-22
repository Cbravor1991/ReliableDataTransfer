from curses import resize_term
from itertools import count
from socket import *
#from rospy import Message

class Segment:
    def __init__(self, message):
        self.message = message
        self.originPort = message[:2]
        self.destPort  = message[2:4] 
        self.length    = message[4:6]
        self.checksum  = message[6:8] 
        

    def checkSumOk(self): # falla el checkout, y no se xq
        return hex(int(self.calculateCheckSum(), 16)) == 0xffff 


    def calculateCheckSum(self):
        print(self.message) # podemos comprobar que recibimos bien el mensaje !
        return self.originPort.decode() + self.destPort.decode() + self.length.decode() + self.checksum.decode()
        
    
def mainServer():
    serverPort = 12000
    serverSocket = socket(AF_INET, SOCK_DGRAM)
    serverSocket.bind(('', serverPort))

    while True:
        segment, clientAddress = serverSocket.recvfrom(2048)
        segment = Segment(segment)

        if not segment.checkSumOk():
            print("Error checkout")
            exit()

        message = len(segment.message.decode())
        modifiedMessage = "La cantidad de letras que tiene la palabra es " + str(message)
        serverSocket.sendto(modifiedMessage.encode(), clientAddress)

mainServer()

