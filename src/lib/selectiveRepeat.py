from receiver import Receiver
from sender import Sender


class SelectiveRepeat:
    
    def __init__(self) -> None:
        pass

    def upload(self, clientSocket, filename, file, fileSize, serverAddr):
        sender = Sender(file, serverAddr[1], fileSize)
        sender.startClient(clientSocket, filename, file, fileSize, serverAddr)

    def download(self):
        receiver = Receiver()
        receiver.receive()

    def downloadFromServer(self):
        sender = Sender(0, serverAddr[0], serverAddr[1])
        sender.startClient(clientSocket, filename, file, fileSize, serverAddr)
    
    def receiveFileFromClient(self, segment, clientAddr):
        receiver = Receiver()
        receiver.receive(segment, clientAddr)


    
    