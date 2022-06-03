import logging
from lib.client import Client
from lib.arguments import parse_client_download
from lib.selectiveRepeat import SelectiveRepeat
from lib.stopAndWait import StopAndWait

def main():
    args, level = parse_client_download()
    GREEN = "\033[1;32m"
    NC = "\033[0m"
    logging.basicConfig(
        level=level,
        format=f"%(asctime)s - [{GREEN}download{NC} %(levelname)s] - %(message)s",
        datefmt="%Y/%m/%d %H:%M:%S",
    )
    serverAddr = (args.host, args.port)

    if (args.protocol.value == 'selectiveRepeat'):
        client = Client('localhost', 0, SelectiveRepeat())
    else:
        client = Client('localhost', 0, StopAndWait())
    try:
        logging.info('Starting download client...')
        client.download(args.filename, args.dst, serverAddr)
    except KeyboardInterrupt:
        logging.info("Shutting down client...")
    except Exception as e:
        logging.warning(f'Exception: {e}')

    logging.info("Client shut down")
    client.shutdown()

main()