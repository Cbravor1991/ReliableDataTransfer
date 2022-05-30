from socketUDP import SocketUDP
from protocol import Protocol
from fileHandler import  FileHandler

ACK = 4

def main():
    
    clientSocket = SocketUDP()
    clientSocket.bindSocket("localhost", 0)
    serverAddress = ("localhost",12000)
    protocol = Protocol()

    fileHandler = FileHandler()
    MSS = 2
    message = 'ABCDEFGHIJKLMNO'
    file_size = len(message)
    file_name = 'name'
    #path = './texto.txt'
    #file_size = fileHandler.getSizeFile(path)    
   
    sequenceNumber = 0
    while True:
        uploadMessage = protocol.createUploadMessage(file_size, file_name)
        protocol.sendMessage(clientSocket, serverAddress, uploadMessage)
        try:
            clientSocket.setTimeOut(0.5) 
            segment, serverAddress = protocol.receive(clientSocket)
            sequenceNumber = protocol.processACKSegment(segment)
            print('ACK {}'.format(sequenceNumber))
            sequenceNumber += 1
            break
        except:
            pass
        
    i = 0
    while i < len(message):
        packageMessage = protocol.createRecPackageMessage(i, MSS, message, sequenceNumber)
        protocol.sendMessage(clientSocket, serverAddress, packageMessage)
        try:
            clientSocket.setTimeOut(0.5) #Que valor poner?
            segment, serverAddress = protocol.receive(clientSocket)
            sequenceNumber = protocol.processACKSegment(segment)
            print('ACK {}'.format(sequenceNumber))
            sequenceNumber += 1
            i += MSS
        except:
            pass


main()



