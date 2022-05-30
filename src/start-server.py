from server import Server


def main():
    server = Server('localhost', 12000)
    try:
        server.start()
    except KeyboardInterrupt:
        print("Shutting down server...")
        server.shutdown()
        print("Server shut down")

main()