from socketUDP import SocketUDP
from protocol import Protocol

def main():
    
    clientSocket = SocketUDP()
    clientSocket.startClient()
    serverAddress = ("localhost",12000)
    protocol = Protocol()

    file_size = 8
    file_name = 'name'


    downloadMessage = protocol.createDownloadMessage(file_name)
    protocol.sendMessage(clientSocket, serverAddress, downloadMessage)

main()
