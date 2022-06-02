from lib.protocol import Protocol
from lib.fileHandler import FileHandler
from socket import timeout

MSS = 200

class StopAndWait:

    def __init__(self) -> None:
        self.protocol = Protocol()
        

    def upload(self, clientSocket, fileName, file, fileSize, serverAddr):
        uploadMessage = self.protocol.createUploadMessage(fileSize, fileName)
        sequenceNumber = self.sendAndReceiveACK(uploadMessage, serverAddr, clientSocket)

        uploaded = 0
        while uploaded < fileSize:
            data = FileHandler.readFileBytes(uploaded, file, MSS)
            print(data, fileSize, uploaded)
            packageMessage = self.protocol.createRecPackageMessage(data, sequenceNumber+1)
            sequenceNumber = self.sendAndReceiveACK(packageMessage, serverAddr, clientSocket)
            print( "len(data) {}".format(len(data)))
            uploaded += min(len(data), MSS)
        print("Upload finished")

    def sendAndReceiveACK(self, msg, serverAddr, clientSocket):
        while True:
            try:
                clientSocket.setTimeOut(1)  
                self.protocol.sendMessage(clientSocket, serverAddr, msg)
                segment, _ = self.protocol.receive(clientSocket)
                # que pasa si se recibe un paquete que no es ACK? deberia saltar excepcion en el decoder
                sequenceNumber = self.protocol.processACKSegment(segment)
                print('ACK {}'.format(sequenceNumber))
                break
            except timeout:
                clientSocket.addTimeOut()
                print("timeout") 
        return sequenceNumber

    def download(self, clientSocket, fileName, path, serverAddr):
        
        file = FileHandler.newFile(str(path), fileName)
        
        downloadMessage = self.protocol.createDownloadMessage(fileName)
        self.sendAndReceiveACK(downloadMessage, serverAddr, clientSocket)
        
        prevSequenceNumber = 0
        morePackages = True
        while morePackages:

            segment, serverAddr = self.protocol.receive(clientSocket)
            sequenceNumber, morePackages, data = self.protocol.processDownloadPackageSegment(segment)
            print('Sequence number {}'.format(sequenceNumber))
            print(data)
            ACKMessage = self.protocol.createACKMessage(sequenceNumber)
            self.protocol.sendMessage(clientSocket, serverAddr, ACKMessage)

            if sequenceNumber > prevSequenceNumber:
                file.write(data)
            prevSequenceNumber = sequenceNumber
        FileHandler.closeFile(file)
        print("Download finished")