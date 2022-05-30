from socketUDP import SocketUDP
from protocol import Protocol
from fileHandler import  FileHandler



ACK = 4

def main():
    
    clientSocket = SocketUDP()
    clientSocket.bindSocket("localhost", 0)
    serverAddress = ("localhost",12000)
    protocol = Protocol()

    fileHandler = FileHandler()
    MSS = 2
    message = 'ABCDEFGHIJKLMNO'
    file_size = len(message)
    file_name = 'name'
    #path = './texto.txt'
    #file_size = fileHandler.getSizeFile(path)    

    uploadMessage = protocol.createUploadMessage(file_size, file_name)
    protocol.sendMessage(clientSocket, serverAddress, uploadMessage)

    # Stop and Wait (implementado en processAck):
    #   Envio y espero ACK
    #   Si no me llega ACK en timeout-> Reenviar
    #   Si llega ACK -> Continuar
    #   Si llega ACK y es el ultimo segmento -> Terminar

    for i in range(0, len(message), MSS):
        packageMessage = protocol.createRecPackageMessage(i, MSS, message)
        protocol.sendMessage(clientSocket, serverAddress, packageMessage)
        segment, serverAddress = protocol.receive(clientSocket) # Llamada bloqueante
        sequenceNumber = protocol.processACKSegment(segment)
        print('ACK {}'.format(sequenceNumber))
        # Si no me llega el ACK luego de timeout tengo que reenviar => Falta implementar


    #for i in range(0, file_size, MSS):
    #    chunks = fileHandler.readFileBytes(path,i)
    #    #ya estaria enviando los bytes
    #    packageMessage = protocol.createRecPackageMessage(i, MSS, chunks)
    #    protocol.sendMessage(clientSocket, serverAddress, packageMessage)
    #    segment, serverAddress = protocol.receive(clientSocket)
    #    sequenceNumber = protocol.processACKSegment(segment)
    #    print('ACK {}'.format(sequenceNumber))
    #    # Si no me llega el ACK luego de timeout tengo que reenviar => Falta implementar




main()



