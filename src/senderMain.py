from sender import Sender


def main():
    sender = Sender('./tp_file_transfer_udp_selective_repeat.pdf', 12000)
    sender.start()


main()
