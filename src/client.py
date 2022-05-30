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

    uploadMessage = protocol.createUploadMessage(file_size, file_name)
    protocol.sendMessage(clientSocket, serverAddress, uploadMessage)

    # Stop and Wait
        # Envio segmento y espero el ACK
        # Si no me llega el ACK -> Timeout -> Reenvio
    
    sequenceNumber = 1
    for i in range(0, len(message), MSS):
        packageMessage = protocol.createRecPackageMessage(i, MSS, message, sequenceNumber)
        protocol.sendMessage(clientSocket, serverAddress, packageMessage)
        try:
            clientSocket.setTimeOut(10) #Que valor poner?
            segment, serverAddress = protocol.receive(clientSocket)
            sequenceNumber = protocol.processACKSegment(segment)
            print('ACK {}'.format(sequenceNumber))
            sequenceNumber += 1
        except:
            i = i - MSS


main()



