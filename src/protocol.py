"""
UploadMessage: 1 | fileSize | fileName
DownloadMessage: 2 | fileName

"""
class Protocol:
    
    def __init__(self) -> None:
        self.upload = bytearray([1])
        self.download = bytearray([2])
        self.packageSize = 10

    def createUploadMessage(self, fileSize, fileName):
        uploadMessage = self.upload
        uploadMessage += (fileSize.to_bytes(4, 'big'))
        uploadMessage += bytearray(fileName, 'utf-8')
        return uploadMessage
    
    def createDownloadMessage(self, fileName):
        downloadMessage = self.download
        downloadMessage += bytearray(fileName, 'utf-8') 
        return downloadMessage


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

    def sendMessage(self, clientSocket, serverAddress, message):
        clientSocket.sendTo(message, serverAddress)
    
    def receive(self, serverSocket):
        segment, clientAddress = serverSocket.receiveFrom(self.packageSize)
        return segment