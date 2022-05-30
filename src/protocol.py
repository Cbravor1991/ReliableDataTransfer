"""
UploadMessage: 1 | fileSize | fileName
DownloadMessage: 2 | fileName

"""

from messageMaker import MessageMaker
from messageProcessor import MessageProcessor

class Protocol:
    
    def __init__(self):
        self.messageMaker = MessageMaker()
        self.messageProcessor = MessageProcessor()

    # Create message
    def createUploadMessage(self, fileSize, fileName):
        return self.messageMaker.createUploadMessage(fileSize, fileName)

    def createDownloadMessage(self, fileName):
        return self.messageMaker.createDownloadMessage(fileName)

    def createRecPackageMessage(self, index, dataSize, message, sequenceNumber):
        data = message[index:(index+dataSize)]
        checkSum = self.calculateCheckSum(data)
        return self.messageMaker.createRecPackageMessage(sequenceNumber, checkSum, data)
    
    def createACKMessage(self, sequenceNumber):
        return self.messageMaker.createACKMessage(sequenceNumber)
    
    # Process message
    def processUploadSegment(self, segment):  
        return self.messageProcessor.processUploadSegment(segment)

    def processDownloadSegment(self, segment):  
        return self.messageProcessor.processDownloadSegment(segment)
    
    def processRecPackageSegment(self, segment):
        return self.messageProcessor.processRecPackageSegment(segment)
    
    def processACKSegment(self, segment):
        return self.messageProcessor.processACKSegment(segment)

    # Send message
    def sendMessage(self, clientSocket, serverAddress, message):
        clientSocket.sendTo(message, serverAddress)
    
    # Receive message
    def receive(self, serverSocket):
        segment, clientAddress = serverSocket.receiveFrom(2048)
        return segment, clientAddress

    # Checksum
    def calculateCheckSum(self, data):
        checkSum = 0
        for i in range(0, len(data)):
            checkSum += ord(data[i])
        return checkSum

    def verifyCheckSum(self, checkSum, data):
        return checkSum == self.calculateCheckSum(data)