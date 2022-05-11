from time import time


class Record:
    def __init__(self, data, msg_type: str, ttl: int):
        self.msg_type = msg_type
        self.ttl = int(ttl, 16) + round(time())
        self.data = data

    def get_length(self) -> str:
        length_in_bytes = len(self.data) // 2
        hex_len_as_str = hex(length_in_bytes)[2:]
        return hex_len_as_str.rjust(4, '0')

    def get_ttl(self) -> str:
        difference = self.ttl - round(time())
        hex_difference_as_str = hex(difference)[2:]
        return hex_difference_as_str.rjust(8, '0')

    def get_data(self):
        return self.data

    def stringify(self):
        return ('c00c' + self.msg_type +
                '0001' + self.get_ttl()
                + self.get_length() + self.data)