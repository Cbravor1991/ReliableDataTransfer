import queue
from lib.protocol import Protocol
from lib.fileHandler import FileHandler
from lib.decoder import Decoder
from socket import timeout
from math import ceil

MSS = 5
N_TIMEOUTS = 20

class StopAndWait:

    def __init__(self) -> None:
        self.protocol = Protocol()
        

    def sendAndReceiveACK(self, msg, addr, recvQueue, sendQueue):
        timeouts = 0
        while True:
            try:
                sendQueue.put((msg, addr))
                segment = recvQueue.get(block=True, timeout=1)
                if Decoder.isTerminate(segment):
                    raise Exception('Closed server')
                # que pasa si se recibe un paquete que no es ACK? deberia saltar excepcion en el decoder
                sequenceNumber = self.protocol.processACKSegment(segment)
                print(f'Download {addr}, server recibe ACK {sequenceNumber}')
                break
            except queue.Empty:
                timeouts += 1
                if timeouts >= N_TIMEOUTS:
                    raise Exception('Timeouts exceeded')
                print("timeout, server no recibe el ack. Se reenvia el paquete") 
        return sequenceNumber
 
    def socketSendAndReceiveACK(self, msg, serverAddr, clientSocket):
        while True:
            try:
                clientSocket.setTimeOut(1) 
                self.protocol.sendMessage(clientSocket, serverAddr, msg)
                segment, _ = self.protocol.receive(clientSocket)
                sequenceNumber = self.protocol.processACKSegment(segment)
                print('cliente recibe el ACK {}'.format(sequenceNumber))
                break
            except timeout:
                clientSocket.addTimeOut()
                print("timeout") 
        return sequenceNumber    

    def socketSendAndReceiveFileSize(self, msg, serverAddr, clientSocket):
        clientSocket.resetTimeout()
        while True:
            try:
                clientSocket.setTimeOut(1) 
                self.protocol.sendMessage(clientSocket, serverAddr, msg)
                segment, _ = self.protocol.receive(clientSocket)
                break
            except timeout:
                clientSocket.addTimeOut()
                print("timeout") 
        return segment    


    def sendAndReceiveData(self, msg, serverAddr, clientSocket):
        while True:
            try:
                clientSocket.setTimeOut(1) 
                self.protocol.sendMessage(clientSocket, serverAddr, msg)
                segment, _ = self.protocol.receive(clientSocket)
                sequenceNumber, morePackages, data = self.protocol.processDownloadPackageSegment(segment)
                break
            except timeout:
                clientSocket.addTimeOut()
                print("timeout, no se recibio el DownloadPackage. Se envia nuevamente el paquete inicial") 
        return sequenceNumber, morePackages, data        

    
    def clientUpload(self, clientSocket, fileName, file, fileSize, serverAddr):

        uploadMessage = self.protocol.createUploadMessage(fileSize, fileName)
        sequenceNumber = self.socketSendAndReceiveACK(uploadMessage, serverAddr, clientSocket)

        uploaded = 0
        while uploaded < fileSize:
            data = FileHandler.readFileBytes(uploaded, file, MSS)
            packageMessage = self.protocol.createRecPackageMessage(data, sequenceNumber+1)
            sequenceNumber = self.socketSendAndReceiveACK(packageMessage, serverAddr, clientSocket)
            print('cliente recibe Sequence number = {}, data = {}'.format(sequenceNumber, data))
            uploaded += min(len(data), MSS)
        print("Upload finished")


    def clientDownload(self, clientSocket, fileName, path, serverAddr):
        
        file = FileHandler.newFile(str(path), fileName)
        
        downloadMessage = self.protocol.createDownloadMessage(fileName)
        prevSequenceNumber, morePackages, data = self.sendAndReceiveData(downloadMessage, serverAddr, clientSocket)
        print('cliente recibe Sequence number = {}, data = {}'.format(prevSequenceNumber, data))
        file.write(data)
        ACKMessage = self.protocol.createACKMessage(prevSequenceNumber)
        self.protocol.sendMessage(clientSocket, serverAddr, ACKMessage)
        
        while morePackages:
            clientSocket.setTimeOut(15)
            segment, serverAddr = self.protocol.receive(clientSocket)
            sequenceNumber, morePackages, data = self.protocol.processDownloadPackageSegment(segment)
            print('cliente recibe Sequence number = {}, data = {}'.format(sequenceNumber, data))
            ACKMessage = self.protocol.createACKMessage(sequenceNumber)
            self.protocol.sendMessage(clientSocket, serverAddr, ACKMessage)

            if sequenceNumber > prevSequenceNumber:
                file.write(data)
            prevSequenceNumber = sequenceNumber
            
        FileHandler.closeFile(file)
        print("Download finished")


    def serverUpload(self, recvQueue, sendQueue, clientAddr, dstPath):
        segment = recvQueue.get()
        fileSize, fileName = self.protocol.processUploadSegment(segment)
        file = FileHandler.newFile(dstPath, fileName)
        
        ACKMessage = self.protocol.createACKMessage(0)
        sendQueue.put((ACKMessage, clientAddr))
        print('command {} fileSize {} fileName {}'.format(segment[0], fileSize, fileName))
        
        transferred = 0
        prevSequenceNumber = 0
        while transferred != fileSize:

            try:
                segment = recvQueue.get(block=True, timeout=15)
            except:
                print(f'Timeouts exceeded: ending thread {clientAddr}...')
                return
            if Decoder.isRecPackage(segment):            
                sequenceNumber, data = self.protocol.processRecPackageSegment(segment)
                print(f'Upload {clientAddr}: server recibe sequence number {sequenceNumber}')

                ACKMessage = self.protocol.createACKMessage(sequenceNumber)
                sendQueue.put((ACKMessage, clientAddr))

                if sequenceNumber > prevSequenceNumber:
                    transferred += len(data)
                    file.write(data)
                prevSequenceNumber = sequenceNumber
            elif Decoder.isUpload(segment):
                sendQueue.put((ACKMessage, clientAddr))
            elif Decoder.isTerminate(segment):
                print(f'Closed server: ending thread {clientAddr}...')
                return


        FileHandler.closeFile(file)
        print('Upload finished')               



    def serverDownload(self, recvQueue, sendQueue, clientAddr, dstPath):
        segment = recvQueue.get()
        fileName = self.protocol.processDownloadSegment(segment)

        print('command {} fileName {}'.format(segment[0], fileName))
        path = dstPath + fileName
        try:
            file = FileHandler.openFile(path)
            fileSize = FileHandler.getFileSize(path)
        except:
            print('File not found')
            return

        numPackages = ceil(fileSize / MSS)
        sequenceNumber = 0
        sent = 0
        morePackages = True
        while sent < fileSize:
            data = FileHandler.readFileBytes(sent, file, MSS)
            sent += min(len(data), MSS)
            morePackages = numPackages > 1
            packageMessage = self.protocol.createDownloadPackageMessage(data, sequenceNumber+1, morePackages)
            print(f'Download {clientAddr}: server envia el paquete {sequenceNumber+1}')
            try:
                sequenceNumber = self.sendAndReceiveACK(packageMessage, clientAddr, recvQueue, sendQueue)
            except Exception as e:
                print(f'{e}: ending thread {clientAddr}...')
                return
            numPackages -= 1

        FileHandler.closeFile(file)
        print("Download finished")