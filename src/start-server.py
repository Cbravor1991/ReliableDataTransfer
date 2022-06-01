import logging
from lib.server import Server
from lib.arguments import parse_server_start

def main():
    args = parse_server_start()
    logging.info(f'storage: {args.dest}')
    server = Server(args.host, args.port)
    try:
        server.start()
    except KeyboardInterrupt:
        print("Shutting down server...")
        server.shutdown()
        print("Server shut down")

main()