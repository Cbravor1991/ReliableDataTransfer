from operator import add
from socket import *

serverName = '127.0.0.1'
serverPort = 12000

# originPort | serverPort | length | checkSum | message

def calculateCheckSum(originPort, destPort, length):
	return ~(originPort + destPort + length)


def getOriginPort(clientSocket):
    return int(getnameinfo(clientSocket.getsockname(), NI_DGRAM)[1])


def getLength(message):
    return len(message) + 8


def getStructureUDP(message, clientSocket):
    originPort = getOriginPort(clientSocket)
    length = getLength(message)
    checkSum = calculateCheckSum(originPort, serverPort, length)
    return [originPort, serverPort, length, checkSum, message]


def addHeader(message, clientSocket):
    structureUDP = getStructureUDP(message, clientSocket)

    segment = ""
    for i in range(len(structureUDP)):
        segment = str(segment) + str(structureUDP[i])
    return segment


def mainClient():
    clientSocket = socket(AF_INET, SOCK_DGRAM)
    clientSocket.bind(("localhost" , 0))
    message = input("Escriba una palabra: ")
   
    segment = addHeader(message, clientSocket)
    print(segment)
    
    clientSocket.sendto(segment.encode(), (serverName, serverPort))
    newMessage, serverAddress = clientSocket.recvfrom(2048)
    
    print(newMessage.decode())
    clientSocket.close()

mainClient()


