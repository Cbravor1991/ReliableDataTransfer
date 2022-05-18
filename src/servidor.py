from itertools import count
from socket import *

serverPort = 12000
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('', serverPort))

while True:
    message, clientAddress = serverSocket.recvfrom(2048)
    message = len(message.decode())
    modifiedMessage = "La cantidad de letras que tiene la palabra es " + str(message)
    print(clientAddress)
    serverSocket.sendto(modifiedMessage.encode(), clientAddress)