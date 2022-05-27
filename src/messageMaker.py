class MessageMaker:

    # Msg = Upload + FileSize + FileName    
    def createUploadMessage(self, fileSize, fileName):
        uploadMessage = bytearray([1])
        uploadMessage += fileSize.to_bytes(4, 'big')
        uploadMessage += bytearray(fileName, 'utf-8')
        return uploadMessage
    
    # Msg = Download + FileName
    def createDownloadMessage(self, fileName):
        downloadMessage = bytearray([2])
        downloadMessage += bytearray(fileName, 'utf-8') 
        return downloadMessage 

    # Msg = recPackage + CheckSum + Data
    def createRecPackageMessage(self, protocol, index, dataSize, message):
        data = message[index:(index+dataSize)]
        packageMessage = bytearray([3])
        packageMessage += protocol.calculateCheckSum(data).to_bytes(2, 'big')
        packageMessage += bytearray(data, 'utf-8')
        return packageMessage 