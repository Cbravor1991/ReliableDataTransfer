import logging
from lib.server import Server
from lib.arguments import parse_server_start


def main():
    args = parse_server_start()
    server = Server(args.host, args.port, args.dest)
    try:
        server.start()
    except KeyboardInterrupt:
        print("Shutting down server...")
    except Exception as e:
        print(e)

    server.shutdown()
    print("Server shut down")


main()
