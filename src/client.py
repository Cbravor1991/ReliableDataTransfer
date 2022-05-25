from socketUDP import SocketUDP
from protocol import Protocol

def main():
    
    clientSocket = SocketUDP()
    clientSocket.bindSocket("localhost", 0)
    serverAddress = ("localhost",12000)
    protocol = Protocol()

    file_size = 4
    file_name = 'name'
    message = 'ABCD'

    uploadMessage = protocol.createUploadMessage(file_size, file_name)
    protocol.sendMessage(clientSocket, serverAddress, uploadMessage)
    protocol.sendChunkMessage(clientSocket, serverAddress, message)

main()
