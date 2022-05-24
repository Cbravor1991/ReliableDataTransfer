"""
UploadMessage: 1 | fileSize | fileName
DownloadMessage: 2 | fileName

"""
class Protocol:
    
    def __init__(self) -> None:
        self.upload = bytearray([1])
        self.download = bytearray([2])
        self.packageSize = 10
        self.recPackage = bytearray([3])
        self.MSS = 2
        
    def createUploadMessage(self, fileSize, fileName):
        uploadMessage = self.upload
        uploadMessage += (fileSize.to_bytes(4, 'big'))
        uploadMessage += bytearray(fileName, 'utf-8')
        return uploadMessage
    
    def createDownloadMessage(self, fileName):
        downloadMessage = self.download
        downloadMessage += bytearray(fileName, 'utf-8') 
        return downloadMessage

        # Msg = recPackage + Data
    def createRecPackageMessage(self, index, dataSize, data):
        packageMessage = bytearray([3])
        packageMessage += bytearray(data[index:(index+dataSize)], 'utf-8')
        return packageMessage

    def processUploadSegment(self, segment):  
        fileSize = int.from_bytes(segment[1:5], 'big')
        fileNameArray = segment[5:9]
        fileName = ""
        for i in range(0,4):
            fileName += chr(fileNameArray[i])
        return (fileSize, fileName)

    def processRecPackageSegment(self, segment):
        dataByte = segment[1:]
        data = ""
        for i in range(0, len(dataByte)):
            data += chr(dataByte[i])
        return (len(data), data)

    def processDownloadSegment(self, segment):  
        fileNameArray = segment[1:5]
        fileName = ""
        for i in range(0,4):
            fileName += chr(fileNameArray[i])
        return fileName

    def sendMessage(self, clientSocket, serverAddress, message):
        clientSocket.sendTo(message, serverAddress)
    
    def receive(self, serverSocket):
        segment, clientAddress = serverSocket.receiveFrom(2048)
        return segment



    def sendChunkMessage(self, clientSocket, serverAddress, message):
        for i in range(0, len(message), self.MSS):
            packageMessage = self.createRecPackageMessage(i, self.MSS, message)
            self.sendMessage(clientSocket, serverAddress, packageMessage)

    