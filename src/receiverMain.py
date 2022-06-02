from receiver import Receiver


def main():
    receiver = Receiver()
    receiver.bindSocket("localhost", 12000)

    receiver.receive()


main()
