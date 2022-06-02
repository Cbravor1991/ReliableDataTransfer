from ast import arg
import enum
import logging
from lib.selectiveRepeat import SelectiveRepeat
from lib.server import Server
from lib.arguments import parse_server_start
from lib.stopAndWait import StopAndWait


def main():
    args = parse_server_start()
    try:
        if (args.protocol.value == 'selectiveRepeat'):
            server = Server(args.host, args.port, args.dest, SelectiveRepeat())
            server.selectiveRepeat()
        else:
            server = Server(args.host, args.port, args.dest, StopAndWait())
            server.stopAndWait()
    except KeyboardInterrupt:
        print("Shutting down server...")
    except Exception as e:
        print(e)

    server.shutdown()
    print("Server shut down")


main()
