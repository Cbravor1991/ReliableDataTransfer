from ast import arg
import enum
import logging
from lib.selectiveRepeat import SelectiveRepeat
from lib.server import Server
from lib.arguments import parse_server_start
from lib.stopAndWait import StopAndWait

def main():
    args = parse_server_start()
    if (args.protocol.value == 'selectiveRepeat'):
        transferMethod = SelectiveRepeat()
    else:
        transferMethod = StopAndWait()

    try:
        server = Server(args.host, args.port, args.dest, transferMethod)
        server.start()

    except KeyboardInterrupt:
        print("Shutting down server...")
    
    except Exception as e:
        print(e)

    server.shutdown()
    print("Server shut down")


main()
