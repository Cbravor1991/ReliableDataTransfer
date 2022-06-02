from protocol import Protocol
from socketUDP import SocketUDP

class Receiver:
    def __init__(self) -> None:
        self.window_size = 5
        self.window_start = 0
        self.messagesBuffer = [False for i in range(1000)]



def main():
    
    serverSocket = SocketUDP()
    serverSocket.bindSocket("localhost", 12000)
    protocol = Protocol()
    receiver = Receiver()


    while True: # hasta terminar el upload o que haya algun error
        
        segment, clientAddr = protocol.receive(serverSocket)
        
        sequenceNumber, checkSum, data = protocol.processRecPackageSegment(segment)
         

        if (sequenceNumber >= receiver.window_start and sequenceNumber < receiver.window_size + receiver.window_start):
            ACKMessage = protocol.createACKMessage(sequenceNumber)
            protocol.sendMessage(serverSocket, clientAddr, ACKMessage)
            print('Sequence number {}, data: {}'.format(sequenceNumber,data))
            receiver.messagesBuffer[sequenceNumber] = data
            if (sequenceNumber == receiver.window_start):
                receiver.window_start += 1
                i = receiver.window_start 
                while i < receiver.window_start + receiver.window_size:
                    if (receiver.messagesBuffer[i] != False):
                        receiver.window_start += 1
                    else:
                        break
                    i += 1
        elif (sequenceNumber < receiver.window_start):
            ACKMessage = protocol.createACKMessage(sequenceNumber)
            protocol.sendMessage(serverSocket, clientAddr, ACKMessage)
        else:
            pass

       


main()