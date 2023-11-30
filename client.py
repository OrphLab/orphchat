import uuid

class Client:
    def __init__(self, socket, address, nickname):
        self.socket = socket
        self.address = address
        self.nickname = nickname
        self.id = uuid.uuid4()
           
    def __str__(self):
        return f"{self.nickname} ({self.address}) {self.id}"