import logging
from lib.client import Client
from lib.fileHandler import FileHandler
from lib.arguments import parse_client_upload
from lib.selectiveRepeat import SelectiveRepeat
from lib.stopAndWait import StopAndWait
from time import sleep

def main():
    args, level = parse_client_upload()
    BLUE = "\033[94m"
    NC = "\033[0m"
    logging.basicConfig(
        level=level,
        format=f"%(asctime)s - [{BLUE}upload{NC} %(levelname)s] - %(message)s",
        datefmt="%Y/%m/%d %H:%M:%S",
    )
    fileSize = FileHandler.getFileSize(args.src) 
    file = FileHandler.openFile(args.src)
    serverAddr = (args.host, args.port)

    if (args.protocol.value == 'selectiveRepeat'):
        transferMethod = SelectiveRepeat()
    else:
        transferMethod = StopAndWait()

    client = Client('localhost', 0, transferMethod)
    try:
        logging.info('Starting upload client...')
        client.upload(args.filename, file, fileSize, serverAddr)
    except KeyboardInterrupt:
        logging.info("Shutting down client...")

    FileHandler.closeFile(file)
    client.shutdown()
    if (args.protocol.value == 'selectiveRepeat'):
        client.transferMethod.sender.active = False
        sleep(1)

    logging.info("Client shut down")


main()