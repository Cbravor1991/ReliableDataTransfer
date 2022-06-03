import logging
from lib.selectiveRepeat import SelectiveRepeat
from lib.server import Server
from lib.arguments import parse_server_start
from lib.stopAndWait import StopAndWait

def main():
    args, level = parse_server_start()
    ORANGE = "\033[0;33m"
    NC = "\033[0m"
    logging.basicConfig(
        level=level,
        format=f"%(asctime)s - [{ORANGE}server{NC} %(levelname)s] - %(message)s",
        datefmt="%Y/%m/%d %H:%M:%S",
    )
    if (args.protocol.value == 'selectiveRepeat'):
        transferMethod = SelectiveRepeat()
    else:
        transferMethod = StopAndWait()

    try:
        logging.info('Starting server...')
        server = Server(args.host, args.port, args.dest, transferMethod)
        server.start()

    except KeyboardInterrupt:
        logging.info("Shutting down server...")
    
    except Exception as e:
        logging.warning(f'Exception: {e}')

    server.shutdown()
    logging.info("Server shut down")


main()
