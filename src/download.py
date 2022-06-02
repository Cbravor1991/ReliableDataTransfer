from yaml import parse
from lib.client import Client
from lib.fileHandler import FileHandler
from lib.arguments import parse_client_download

def main():
    args = parse_client_download()

    serverAddr = (args.host, args.port)
    client = Client('localhost', 0)
    try:
        client.download(args.filename, args.dst, serverAddr)
    except KeyboardInterrupt:
        print("Shutting down client...")
    except Exception as e:
        print(e)

    print("Client shut down")
    client.shutdown()

main()