from socketUDP import SocketUDP
from protocol import Protocol

def main():
    
    clientSocket = SocketUDP()
    clientSocket.bindSocket("localhost", 0)
    serverAddress = ("localhost",12000)
    protocol = Protocol()

<<<<<<< HEAD
    file_size = 8
    file_name = 'name'


    downloadMessage = protocol.createDownloadMessage(file_name)

    uploadMessage = protocol.createUploadMessage(file_size, file_name)

    protocol.sendMessage(clientSocket, serverAddress, uploadMessage)
=======
    message = 'ABCDEFGHI'
    file_size = len(message)
    file_name = 'zbcd'

    #UPLOAD
    uploadMessage = protocol.createUploadMessage(file_size, file_name)
    protocol.sendMessage(client, serverAddress, uploadMessage)

    #DOWNLOAD
    #downloadMessage = protocol.createDownloadMessage(file_name)
    #protocol.sendMessage(client, serverAddress, downloadMessage)

    #RECDATA
    protocol.sendChunkMessage(client, serverAddress, message)

   
>>>>>>> bee0311a48723533c872220e02f0157a58dc7696

main()
