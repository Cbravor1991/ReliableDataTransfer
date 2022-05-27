"""
UploadMessage: 1 | fileSize | fileName
DownloadMessage: 2 | fileName

"""

from messageMaker import MessageMaker
from messageProcessor import MessageProcessor

class Protocol:
    
    def __init__(self):
        self.packageSize = 10
        self.MSS = 2
        self.messageMaker = MessageMaker()
        self.messageProcessor = MessageProcessor()

    # Create message
    def createUploadMessage(self, fileSize, fileName):
        return self.messageMaker.createUploadMessage(fileSize, fileName)

    def createDownloadMessage(self, fileName):
        return self.messageMaker.createDownloadMessage(fileName)

    def createRecPackageMessage(self, index, dataSize, message):
        return self.messageMaker.createRecPackageMessage(self, index, dataSize, message)
    
    # Process message
    def processUploadSegment(self, segment):  
        return self.messageProcessor.processUploadSegment(segment)

    def processDownloadSegment(self, segment):  
        return self.messageProcessor.processDownloadSegment(segment)
    
    def processRecPackageSegment(self, segment):
        return self.messageProcessor.processRecPackageSegment(segment)

    # Send message
    def sendMessage(self, clientSocket, serverAddress, message):
        clientSocket.sendTo(message, serverAddress)
    
    def sendChunkMessage(self, clientSocket, serverAddress, message):
        for i in range(0, len(message), self.MSS):
            packageMessage = self.createRecPackageMessage(i, self.MSS, message)
            self.sendMessage(clientSocket, serverAddress, packageMessage)
    
    # Receive message
    def receive(self, serverSocket):
        segment, clientAddress = serverSocket.receiveFrom(2048)
        return segment

    # Checksum
    def calculateCheckSum(self, data):
        checkSum = 0
        for i in range(0, len(data)):
            checkSum += ord(data[i])
        return checkSum

    def verifyCheckSum(self, checkSum, data):
        return checkSum == self.calculateCheckSum(data)