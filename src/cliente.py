from operator import add
from socket import *
import argparse

def parse_arguments():
  
  parser = argparse.ArgumentParser()  
  #parser.add_argument('-h' , "--help", help = "show this help message and exit")
  #parser.add_argument('-v' , '-- verbose', help = 'increase output verbosity')
  #parser.add_argument('-q' , '-- quiet', help= 'decrease output verbosity')
  parser.add_argument('-H' , '--host', default= "127.0.0.1",  help = 'service IP address')
  parser.add_argument('-p' , '--port', default=8080, help=  'service port')
  #parser.add_argument('-s' , '-- storage' help= 'storage dir path', required=True)
  
  
  return parser.parse_args()


class RDTclient:
    def __init__(self, message, originPort, serverPort):
        self.message = int(message, 16) # supongamos que es un entero 
        self.originPort = int(originPort, 16) & 0xffff
        self.destinationPort = int(serverPort, 16) & 0xffff
        self.length = int(12, 16) & 0xffff #4 bytes numero + 8 bytes head

    def calculateCheckSum(self):
        return ~(self.originPort + self.destinationPort + self.length) # adicionar message

    def getStructureUDP(self):
        return [self.originPort, self.destinationPort, self.length, self.calculateCheckSum(), self.message]

    def multiplex(self):
        structureUDP = self.getStructureUDP()
        segment = ""
        for i in range(len(structureUDP)-1):
            segment = structureUDP[i] << 8 + structureUDP[i+1] #retocar esto para que funcione

        for i in range(len(structureUDP)): #veo que envio
            print(structureUDP[i])

        return segment.encode()



def mainClient():
    args = parse_arguments()
    message = int(input("Escriba un numero: ")) #supongo que mando 4 bytes
    
    serverName = args.host
    serverPort = args.port
    address = (serverName, serverPort)

    clientSocket = socket(AF_INET, SOCK_DGRAM)
    clientSocket.bind(("localhost" , 0))
    originPort = int(getnameinfo(clientSocket.getsockname(), NI_DGRAM)[1])


    rdtClient = RDTclient(message, originPort, serverPort)
    segment = rdtClient.multiplex()

    print(segment)
        
    clientSocket.sendto(segment, address)
    newMessage, serverAddress = clientSocket.recvfrom(2048)
        
    print(newMessage.decode())
    clientSocket.close()

mainClient()