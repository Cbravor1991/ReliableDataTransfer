from sender import Sender


def main():
    sender = Sender('./texto.txt', 12000)
    sender.start()


main()
