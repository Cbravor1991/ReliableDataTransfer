from yaml import parse
from lib.client import Client
from lib.fileHandler import FileHandler
from lib.arguments import parse_client_download
from lib.selectiveRepeat import SelectiveRepeat
from lib.stopAndWait import StopAndWait

def main():
    args = parse_client_download()

    serverAddr = (args.host, args.port)

    if (args.protocol.value == 'selectiveRepeat'):
        client = Client('localhost', 0, SelectiveRepeat())
    else:
        client = Client('localhost', 0, StopAndWait())
    try:
        client.download(args.filename, args.dst, serverAddr)
    except KeyboardInterrupt:
        print("Shutting down client...")
    except Exception as e:
        print("ACA")
        print(e)

    print("Client shut down")
    client.shutdown()

main()