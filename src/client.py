from socketUDP import SocketUDP
from protocol import Protocol

def main():
    
    clientSocket = SocketUDP()
    clientSocket.bindSocket("localhost", 0)
    serverAddress = ("localhost",12000)
    protocol = Protocol()

    file_size = 8
    file_name = 'name'


    downloadMessage = protocol.createDownloadMessage(file_name)

    uploadMessage = protocol.createUploadMessage(file_size, file_name)

    protocol.sendMessage(clientSocket, serverAddress, uploadMessage)

main()
