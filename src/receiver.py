from lib.protocol import Protocol
from lib.socketUDP import SocketUDP
import math

class Receiver:
    def __init__(self):
        self.window_size = 200
        self.window_start = 0
        self.messagesBuffer = []
        self.socket = SocketUDP()
        self.protocol = Protocol()

    def bindSocket(self, host, port):
        self.socket.bindSocket(host, port)

    def getTopOfWindow(self, file_size):
        window_top = self.window_start + self.window_size
        file_top = math.ceil(file_size/200)
        if (window_top > file_top):
            return file_top
        else:
            return window_top


    def receive(self):

        
        #segment, clientAddr = self.protocol.receive(self.socket)
        #fileSize, fileName = self.protocol.processUploadSegment(segment)
        #ACKMessage = self.protocol.createACKMessage(0)
        #self.protocol.sendMessage(self.socket, clientAddr, ACKMessage)
        fileName = "Elarhivo0.pdf"
        fileSize = 458533

        file = open(fileName, "wb")
        counter = 0
        self.messagesBuffer = [False for i in range(math.ceil(fileSize/200))]
        while counter < math.ceil(fileSize/200):

            segment, clientAddr = self.protocol.receive(self.socket)

            seqNum, data = self.protocol.processRecPackageSegment(segment)

            if (seqNum >= self.window_start and
               seqNum < self.window_size + self.window_start):

                ACKMessage = self.protocol.createACKMessage(seqNum)
                self.protocol.sendMessage(self.socket, clientAddr, ACKMessage)
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
                ACKMessage = self.protocol.createACKMessage(seqNum)
                self.protocol.sendMessage(self.socket, clientAddr, ACKMessage)
            else:
                pass
            print(counter)
        file.close()
