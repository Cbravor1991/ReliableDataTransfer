from clientUDP import ClientUDP
from protocol import Protocol

def main():
    client = ClientUDP()
    client.startClient()
    serverAddress = ("localhost",12000)
    protocol = Protocol()

    file_size = 8
    file_name = 'zbcd'
    downloadMessage = protocol.createDownloadMessage(file_name)
    #uploadMessage = protocol.createUploadMessage(file_size, file_name)
    protocol.sendMessage(client, serverAddress, downloadMessage)

main()
