"""
UploadMessage: 1 | fileSize | fileName
DownloadMessage: 2 | fileName

"""

from encoder import Encoder
from decoder import Decoder

class Protocol:
    
    def __init__(self):
        self.sequenceNumber = 0
        self.encoder = Encoder()
        self.decoder = Decoder()

    # Create message
    def createUploadMessage(self, fileSize, fileName):
        return self.encoder.createUploadMessage(fileSize, fileName)

    def createDownloadMessage(self, fileName):
        return self.encoder.createDownloadMessage(fileName)

    def createRecPackageMessage(self, data, sequenceNumber):
       
        checkSum = self.calculateCheckSum(data)
        return self.encoder.createRecPackageMessage(sequenceNumber, checkSum, data)
    
    def createACKMessage(self, sequenceNumber):
        return self.encoder.createACKMessage(sequenceNumber)
    
    # Process message
    def processUploadSegment(self, segment):  
        return self.decoder.processUploadSegment(segment)

    def processDownloadSegment(self, segment):  
        return self.decoder.processDownloadSegment(segment)
    
    def processRecPackageSegment(self, segment):
        return self.decoder.processRecPackageSegment(segment)
    
    def processACKSegment(self, segment):
        return self.decoder.processACKSegment(segment)

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