from struct import pack
from lib.decoder import UPLOAD, DOWNLOAD,RECPACKAGE,ACK,DOWNLOADPACKAGE,FILESIZE,TERMINATE

class Encoder:
  
    # Msg = typeUpload + FileSize + FileName    
    def createUploadMessage(self, fileSize, fileName):
        uploadMessage = bytearray([UPLOAD])
        uploadMessage += pack(">i",fileSize)
        uploadMessage += bytearray(fileName, 'utf-8')
        return uploadMessage
    
    def createFileSize(fileSize):
        fileSizeMsg = bytearray([FILESIZE])
        fileSizeMsg += pack(">i",fileSize)
        return fileSizeMsg

    # Msg = typeDownload + FileName
    def createDownloadMessage(self, fileName):
        downloadMessage = bytearray([DOWNLOAD])
        downloadMessage += bytearray(fileName, 'utf-8') 
        return downloadMessage 

    # Msg = typeRecPackage + sequenceNumber +  Data
    def createRecPackageMessage(self, sequenceNumber, data):
        packageMessage = bytearray([RECPACKAGE])
        packageMessage += pack(">H",sequenceNumber)
        packageMessage += data
        return packageMessage

    # Msg = typeRecPackage + sequenceNumber + M + Data
    def createDownloadPackageMessage(self, sequenceNumber, m, data):
        packageMessage = bytearray([DOWNLOADPACKAGE])
        packageMessage += pack(">H",sequenceNumber)
        packageMessage += pack(">B",m)
        packageMessage += data
        return packageMessage

    # Msg = typeACK + sequenceNumber
    def createACKMessage(self, sequenceNumber):
        ACKMessage = bytearray([ACK])
        ACKMessage += pack(">H",sequenceNumber)
        return ACKMessage

    # Msg = typeTerminate
    def createTerminateMessage():
        return bytearray([TERMINATE])