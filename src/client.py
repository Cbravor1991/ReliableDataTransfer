from clientUDP import ClientUDP
from protocol import Protocol

def main():
    client = ClientUDP()
    client.startClient()
    serverAddress = ("localhost",12000)
    protocol = Protocol()

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

   

main()
