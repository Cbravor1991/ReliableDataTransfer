from receiver import Receiver
from sender import Sender


class SelectiveRepeat:
    
    def __init__(self) -> None:
        self.receiver = Receiver()
        self.sender = Sender()

    def upload(self):
        self.sender.start()

    def download(self):
      self.receiver.start()


    
    