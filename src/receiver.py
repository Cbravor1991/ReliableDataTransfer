from lib.decoder import Decoder
from lib.protocol import Protocol
from lib.socketUDP import SocketUDP
import math

MSS = 5
class Receiver:
    def __init__(self):
        self.window_size = 3
        self.window_start = 0
        self.messagesBuffer = []
        self.socket = SocketUDP()
        self.protocol = Protocol()

    def bindSocket(self, host, port):
        self.socket.bindSocket(host, port)

    def getTopOfWindow(self, file_size):
        window_top = self.window_start + self.window_size
        file_top = math.ceil(file_size/MSS)
        if (window_top > file_top):
            return file_top
        else:
            return window_top


    def receive(self, segment, clientAddr, serverSocket):

        fileSize, fileName = self.protocol.processUploadSegment(segment)
        ACKMessage = self.protocol.createACKMessage(0)
        self.protocol.sendMessage(serverSocket, clientAddr, ACKMessage)
        file = open(fileName, "wb")
        counter = 0
        
        self.messagesBuffer = [False for i in range(math.ceil(fileSize/MSS))]
        while counter < math.ceil(fileSize/MSS):
            segment, clientAddr = self.protocol.receive(serverSocket)
            print("Recibo segmento {}".format(segment))
            if (Decoder.isRecPackage(segment)):
                
                seqNum, data = self.protocol.processRecPackageSegment(segment)
                print("Recibo: {}".format(seqNum))
                print(self.window_start)
                if (seqNum >= self.window_start and
                seqNum < self.window_size + self.window_start):

                    ACKMessage = self.protocol.createACKMessage(seqNum)
                
                    self.protocol.sendMessage(serverSocket, clientAddr, ACKMessage)
                    print('Sequence number {}, data: {}'
                        .format(seqNum, data))
                    self.messagesBuffer[seqNum] = data
                    if (seqNum == self.window_start):
                        counter += 1
                        file.write(self.messagesBuffer[seqNum])
                        self.window_start += 1
                        i = self.window_start
                        while i < self.getTopOfWindow(fileSize):
                            if (self.messagesBuffer[i] is not False):
                                self.window_start += 1
                                counter += 1
                                file.write(self.messagesBuffer[i])
                            else:
                                break
                            i += 1
                elif (seqNum < self.window_start):
                    print("Mando por debajo de la ventana {}".format(seqNum))
                    ACKMessage = self.protocol.createACKMessage(seqNum)
                    self.protocol.sendMessage(serverSocket, clientAddr, ACKMessage)
                else:
                    pass
            elif (Decoder.isUpload(segment)):
                self.protocol.sendMessage(serverSocket, clientAddr, ACKMessage)
        file.close()


    def receiveFileFromServer(self, clientSocket, fileName, path, serverAddr):
        downloadMsg = self.protocol.createDownloadMessage(fileName)
        self.protocol.sendMessage(clientSocket, serverAddr, downloadMsg)
        segment, serverAddr = self.protocol.receive(clientSocket)
        fileSize = Decoder.processFileSize(segment)


        file = open(path, "wb")
        counter = 0
        
        self.messagesBuffer = [False for i in range(math.ceil(fileSize/MSS))]
        #self.messagesBuffer = [False for i in range(10000)]
        while counter < math.ceil(fileSize/MSS):
        
        #while counter < math.ceil(10000):
            segment, serverAddr = self.protocol.receive(clientSocket)
            print("Recibo segmento {}".format(segment))
            if (Decoder.isRecPackage(segment)):
                
                seqNum, data = self.protocol.processRecPackageSegment(segment)
                print("Recibo: {}".format(seqNum))
                print(self.window_start)
                if (seqNum >= self.window_start and
                seqNum < self.window_size + self.window_start):

                    ACKMessage = self.protocol.createACKMessage(seqNum)
                
                    self.protocol.sendMessage(clientSocket, serverAddr, ACKMessage)
                    print('Sequence number {}, data: {}'
                        .format(seqNum, data))
                    self.messagesBuffer[seqNum] = data
                    if (seqNum == self.window_start):
                        
                        counter += 1
                        file.write(self.messagesBuffer[seqNum])
                        self.window_start += 1
                        i = self.window_start
                        while i < self.getTopOfWindow(fileSize):
                            if (self.messagesBuffer[i] is not False):
                                self.window_start += 1
                                counter += 1
                                file.write(self.messagesBuffer[i])
                            else:
                                break
                            i += 1
                elif (seqNum < self.window_start):
                    print("Mando por debajo de la ventana {}".format(seqNum))
                    ACKMessage = self.protocol.createACKMessage(seqNum)
                    self.protocol.sendMessage(clientSocket, serverAddr, ACKMessage)
                else:
                    pass
        file.close()
