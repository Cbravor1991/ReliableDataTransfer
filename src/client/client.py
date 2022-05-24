from clientUDP import ClientUDP
from protocol import Protocol

def main():
    client = ClientUDP()
    client.startClient()
    serverAddress = ("localhost",12000)
    protocol = Protocol()


    protocol.startUpload(client, serverAddress)

main()
