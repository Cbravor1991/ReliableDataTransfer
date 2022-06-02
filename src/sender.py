
from threading import Timer
from time import sleep
from socketUDP import SocketUDP
from protocol import Protocol
import threading
from fileHandler import FileHandler

class Sender:
    def __init__(self):
        self.window_size = 5
        self.window_start = 0
        self.messagesBuffer = [False for i in range(self.window_size + 1000)]
        self.printBuffer = [False for i in range(self.window_size + 1000)]
        self.timers = [False for i in range(self.window_size + 1000)]
        self.socket = SocketUDP()
        self.protocol = Protocol()
        self.serverAddress = ("localhost",12000)
        self.fileHandler = FileHandler()
        self.file = self.fileHandler.openFile('./texto.txt')
        self.file_size = self.fileHandler.getSizeFile('./texto.txt')
        self.file_transfered = 0
        self.currentSequenceNumber = 0
        self.lock = threading.Lock()
        self.MSS = 6

    def callFromTimeout(self, index):
        if (self.messagesBuffer[index] != False):
            print('TimeOut SEQ: {}'.format(index))
            self.protocol.sendMessage(self.socket, self.serverAddress, self.messagesBuffer[index])
            self.start_timer(index)

    def removeMessage(self, index):
        self.lock.acquire(blocking=True)
        self.messagesBuffer[index] = None

        self.lock.release()

    def start_timer(self, index):
        self.lock.acquire(blocking=True)
        self.timers[index] = Timer(2, self.callFromTimeout, args=(index,))
        self.timers[index].start()
        self.lock.release()

    def stop_timer(self, index):
        self.lock.acquire(blocking=True)
        if (not self.timers[index]):
            print("ERROR")
        elif(self.timers[index].is_alive()):
            self.timers[index].cancel()
        self.timers[index] = False
        self.lock.release()

    def receivePack(self):
        while True:
            segment, serverAddress = self.protocol.receive(self.socket)
            sequenceNumber = self.protocol.processACKSegment(segment)
            print('ACK: {}'.format(sequenceNumber))


            
            if (sequenceNumber == self.window_start):
                print('ACK BASE: {}'.format(sequenceNumber))

                
                self.stop_timer(sequenceNumber)
                self.removeMessage(sequenceNumber)
                

                self.window_start += 1
                for i in range(self.window_start, self.window_start + self.window_size):
                    if  (self.messagesBuffer[i] == "buffered"):
                        self.window_start += 1
                    
                    else:
                        print("WINDOW START: {}".format(self.window_start))
                        break
            elif (sequenceNumber > self.window_start and sequenceNumber < self.window_start + self.window_size):
                self.stop_timer(sequenceNumber)
                self.removeMessage(sequenceNumber)
                self.messagesBuffer[sequenceNumber] = "buffered"
                self.printBuffer[sequenceNumber] = "buffered"
    

    def readFile(self, index):
        MSS = 6
        return self.fileHandler.readFileBytes(index * MSS, self.file, MSS)
   

    def isNotFullMessageBuffer(self, seqNumber):
        total_messages = 0
        for i in range(self.window_start, self.window_start + self.window_size):
            if (self.messagesBuffer[i] != False):
                total_messages += 1

        return total_messages <= self.window_size and (seqNumber < self.window_start + self.window_size)


    def sendPack(self):
        while self.file_transfered < self.file_size:
            
        
            print("WINDOW {}".format(self.printBuffer[self.window_start:self.window_start + self.window_size]))
            
            if(self.isNotFullMessageBuffer(self.currentSequenceNumber)):
                data = self.readFile(self.currentSequenceNumber)    
                packageMessage = self.protocol.createRecPackageMessage(data, self.currentSequenceNumber)
                self.protocol.sendMessage(self.socket, self.serverAddress, packageMessage)

                self.messagesBuffer[self.currentSequenceNumber] = packageMessage
                self.printBuffer[self.currentSequenceNumber] = self.currentSequenceNumber
                self.start_timer(self.currentSequenceNumber)
                
                print('Sent seq: {}'.format(self.currentSequenceNumber))
                self.currentSequenceNumber += 1
                self.file_transfered += len(data)
            else:
                print("Message Buffer Full")
                sleep(0.5)    


    def start(self):
        self.socket.bindSocket("localhost", 0)

        send_thread = threading.Thread(target=self.sendPack)
        rec_thread = threading.Thread(target=self.receivePack)



        rec_thread.start()
        send_thread.start()


        send_thread.join()
        rec_thread.join()


