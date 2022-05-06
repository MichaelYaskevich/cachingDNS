from time import time


class Record:
    def __init__(self, data, msg_type: str, ttl: int):
        self.msg_type = msg_type
        self.ttl = int(ttl, 16) + int(round(time()))
        self.data = data

    def get_length(self) -> str:
        return hex(len(self.data) // 2)[2:].rjust(4, '0')

    def get_ttl(self) -> str:
        return hex(self.ttl - int(round(time())))[2:].rjust(8, '0')

    def stringify(self):
        return ('c00c' + self.msg_type +
                '0001' + self.get_ttl()
                + self.get_length() + self.data)