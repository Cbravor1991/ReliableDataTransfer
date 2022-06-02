from lib.protocol import Protocol
from lib.socketUDP import SocketUDP


class Receiver:
    def __init__(self):
        self.window_size = 5
        self.window_start = 0
        self.messagesBuffer = [False for i in range(1000)]
        self.socket = SocketUDP()
        self.protocol = Protocol()

    def bindSocket(self, host, port):
        self.socket.bindSocket("localhost", 12000)

    def receive(self):
        while True:

            segment, clientAddr = self.protocol.receive(self.socket)

            seqNum, cs, data = self.protocol.processRecPackageSegment(segment)

            if (seqNum >= self.window_start and
               seqNum < self.window_size + self.window_start):

                ACKMessage = self.protocol.createACKMessage(seqNum)
                self.protocol.sendMessage(self.socket, clientAddr, ACKMessage)
                print('Sequence number {}, data: {}'
                      .format(seqNum, data))
                self.messagesBuffer[seqNum] = data
                if (seqNum == self.window_start):
                    self.window_start += 1
                    i = self.window_start
                    while i < self.window_start + self.window_size:
                        if (self.messagesBuffer[i] is not False):
                            self.window_start += 1
                        else:
                            break
                        i += 1
            elif (seqNum < self.window_start):
                ACKMessage = self.protocol.createACKMessage(seqNum)
                self.protocol.sendMessage(self.socket, clientAddr, ACKMessage)
            else:
                pass
