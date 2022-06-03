from struct import pack


class Encoder:
  
    # Msg = typeUpload + FileSize + FileName    
    def createUploadMessage(self, fileSize, fileName):
        uploadMessage = bytearray([1])
        uploadMessage += pack(">i",fileSize)
        uploadMessage += bytearray(fileName, 'utf-8')
        return uploadMessage
    
    # Msg = typeDownload + FileName
    def createDownloadMessage(self, fileName):
        downloadMessage = bytearray([2])
        downloadMessage += bytearray(fileName, 'utf-8') 
        return downloadMessage 

    # Msg = typeRecPackage + sequenceNumber +  Data
    def createRecPackageMessage(self, sequenceNumber, data):
        packageMessage = bytearray([3])
        packageMessage += pack(">H",sequenceNumber)
        packageMessage += data
        return packageMessage

    # Msg = typeRecPackage + sequenceNumber + M + Data
    def createDownloadPackageMessage(self, sequenceNumber, m, data):
        packageMessage = bytearray([5])
        packageMessage += pack(">H",sequenceNumber)
        packageMessage += pack(">B",m)
        packageMessage += data
        return packageMessage

    # Msg = typeACK + sequenceNumber
    def createACKMessage(self, sequenceNumber):
        ACKMessage = bytearray([4])
        ACKMessage += pack(">H",sequenceNumber)
        return ACKMessage