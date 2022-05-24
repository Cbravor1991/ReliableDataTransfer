class Protocol:

    def __init__(self) -> None:
        self.upload = bytearray([1])
        self.download = bytearray([2])

    def startUpload(self, clientSocket, serverAddress):
        clientSocket.sendTo(self.upload, serverAddress)
    
    def receiveCommandFromClient(self, serverSocket):
        segment, clientAddress = serverSocket.receiveFrom(1)
        return (int.from_bytes(segment, 'big'), clientAddress)