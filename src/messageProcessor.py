class MessageProcessor:

    # Msg = Upload + FileSize + FileName    
    def processUploadSegment(self, segment):  
        fileSize = int.from_bytes(segment[1:5], 'big')
        fileNameArray = segment[5:9]
        fileName = ""
        for i in range(0,4):
            fileName += chr(fileNameArray[i])
        return (fileSize, fileName)

    # Msg = Download + FileName
    def processDownloadSegment(self, segment):  
        fileNameArray = segment[1:5]
        fileName = ""
        for i in range(0,4):
            fileName += chr(fileNameArray[i])
        return fileName

    # Msg = recPackage + CheckSum + Data
    def processRecPackageSegment(self, segment):
        checkSum = int.from_bytes(segment[1:3], 'big')
        dataByte = segment[3:]
        data = ""
        for i in range(0, len(dataByte)):
            data += chr(dataByte[i])
        return (checkSum, data)

  
    