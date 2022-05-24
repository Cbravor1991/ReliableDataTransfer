class Protocol:
    
    def __init__(self) -> None:
        self.upload = bytearray([1])
        self.download = bytearray([2])
        self.packageSize = 10

    # Msg = Upload/Download[1] + FileSize[4] + FileName[4]
    def createUploadMessage(self, fileSize, fileName):
        uploadMessage = self.upload
        uploadMessage += (fileSize.to_bytes(4, 'big'))
        uploadMessage += bytearray(fileName, 'utf-8')
        print(uploadMessage)
        return uploadMessage
    
    def createDownloadMessage(self, fileName):
        downloadMessage = self.download
        # largo del nombre?
        downloadMessage += bytearray(fileName, 'utf-8') 
        return downloadMessage

    def sendMessage(self, clientSocket, serverAddress, message):
        clientSocket.sendTo(message, serverAddress)
    
    def receiveCommand(self, serverSocket):
        command, clientAddress = serverSocket.receiveFrom(1)
        return int(command[0])

    def receive(self, serverSocket):
        segment, clientAddress = serverSocket.receiveFrom(self.packageSize)
        return segment

    def processUploadSegment(self, segment):  
        fileSize = int.from_bytes(segment[1:5], 'big')
        fileNameArray = segment[5:9]
        fileName = ""
        for i in range(0,4):
            fileName += chr(fileNameArray[i])
        return (fileSize, fileName)

    def processDownloadSegment(self, segment):  
        fileNameArray = segment[1:5]
        fileName = ""
        for i in range(0,4):
            fileName += chr(fileNameArray[i])
        return fileName