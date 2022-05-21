from curses import resize_term
from itertools import count
from socket import *

from rospy import Message

serverPort = 12000
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('', serverPort))


class Message:
    def __init__(self, message):
        self.message = message
        self.originPort = message[:2]
        self.destPort  = message[2:4] 
        self.length    = message[4:6]
        self.checksum  = message[6:8] 
        

    def checkSumOk(self):
        return self.checksum == self.calculateCheckSum()

    def calculateCheckSum(self):
        print(self.message)
        for i in range(2): 
            res =  self.originPort[i] + self.destPort[i] + self.length[i] + self.checksum[i]
        print(res)
        
    
        


while True:
    message, clientAddress = serverSocket.recvfrom(2048)
    mess = Message(message)
    if  not mess.checkSumOk():
        exit()
    message = len(message.decode())
    modifiedMessage = "La cantidad de letras que tiene la palabra es " + str(message)
    print(clientAddress)
    serverSocket.sendto(modifiedMessage.encode(), clientAddress)


