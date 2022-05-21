from operator import add
from socket import *

serverName = '127.0.0.1'
serverPort = 12000

def calculateCheckSum(originPort, destPort, length):
	return ~(originPort + destPort + length)

def addHeader(message,clientSocket):
    originPort = getnameinfo(clientSocket.getsockname(),NI_DGRAM)[1]
    return str(serverPort) + str(originPort) + str(len(message)) + str(calculateCheckSum(int(originPort), serverPort, len(message))) + message

clientSocket = socket(AF_INET, SOCK_DGRAM)
clientSocket.bind(("localhost" , 0))
message = input("Escriba una palabra: ")
msg_complete = addHeader(message,clientSocket)
clientSocket.sendto(msg_complete.encode(), (serverName, serverPort))
modifiedMessage, serverAddress = clientSocket.recvfrom(2048)
print(modifiedMessage.decode())
clientSocket.close()


