from curses import resize_term
from itertools import count
from socket import *
import argparse
from pathlib import Path
# importamos las funciones para manejar archivos que vamos a usar en el servidor
from auxiliar.ManejadorArchivos import crear_directorio

def upload(sock, address, storage_dir, file_info):
    return 0

def download(sock, address, storage_dir, file_info):
    return 0   

def start_server(server_address, storage):
    #enviamos un mensaje para informar de que se inicio el servidor
    print('Incio del servidor ({}, {})'.format(server_address, storage))

    #creamos el socket y bindeamos la direccion del servidor
    serverSocket = socket(AF_INET, SOCK_DGRAM)
    serverSocket.bind(server_address)

    while True:
        ''' settimeout(None): por defecto el socket está en modo bloqueante, es decir, 
        las operaciones bloqueantes como recv no van a retornar hasta que no se completen 
        (en el caso de recv hasta que no exista algo que leer en el buffer), quedando el 
        proceso a la espera en ese punto, a no ser que el sistema lance alguna excepción. 
        Equivalente a sock.setblocking(True).'''
        serverSocket.settimeout(None)
        '''Utiliza recvfrom para saber a quién debe devolver los datos.
        En cuanto a si usar 1024 o 2048,  estos representan la cantidad de bytes que desea aceptar.
         En términos generales, UDP tiene menos gastos generales que TCP, lo que le permite recibir 
         más datos, pero esta no es una regla estricta y es casi insignificante en este contexto. 
         Puede recibir tanto o tan poco como desee. 4096 también es común (para ambos). '''
        segment, client_address = serverSocket.recvfrom(1024)
        segment = segment.decode()
        #imprimimos mensaje de que recibimos solicitud
        print(print("Solicitud recibida de  {} para accionar {}".format(client_address, segment)))
        try:
            
            command, file_info = segment.split("|", 1)
        except ValueError:
            print("No se reconoce mensaje del cliente para la direccion {}. El segmento es {}".format(client_address, segment))
            continue

        if command == 'upload':
            upload(serverSocket, client_address, storage, file_info)
        elif command == 'download':
            download(serverSocket, client_address, storage, file_info)
        else:
            print("El comando {} no es reconocido".format(command))
            continue

        serverSocket.close()


    


def manejoDeArgumentos():
    manejador = argparse.ArgumentParser()
    #-h , -- help show this help message and exit
    #-v , -- verbose increase output verbosity
    #-q , -- quiet decrease output verbosity
    #-H , -- host service IP address
    #-p , -- port service port
    #-s , -- storage storage dir path
    
    manejador.add_argument("-H", "--host", default= "127.0.0.1", help = "direccion ip del servidor")
    manejador.add_argument("-p", "--port", default= 8080, help = "puerto del sevidor")
    manejador.add_argument("-s", "--storage", help= "ruta del directorio de almacenamiento", required = True)

    return manejador.parse_args()

#inicio del servidor
def main():
    #solicitamos los argumentos ingresados por consola
    args = manejoDeArgumentos() 
    #iniciamos la tupla con el host y el port
    server_address = (args.host, args.port)
    #comenzamos el servidor udp llamando al funcion 
    start_server (server_address, args.storage)


main()



