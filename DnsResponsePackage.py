import binascii
import struct
from time import time

from help_methods import *

byte_len = 2
header_in_bytes_len = 12
header_as_str_len = 24
encoding = "utf-8"


class DnsResponsePackage:
    def __init__(self, data_in_bytes):
        self._data_in_bytes = data_in_bytes
        self._data_as_str = convert_to_str(self._data_in_bytes)

        header, body = data_in_bytes[:header_in_bytes_len], data_in_bytes[header_in_bytes_len:]
        unpacked_header = struct.unpack("2s2s2s2s2s2s", header)
        self._ID, self._flags, self._QDCOUNT, self._ANCOUNT, self._NSCOUNT, self._ARCOUNT = \
            [convert_to_str(x) for x in unpacked_header]

        (self._qname, self._qtype, self._qclass) = self.__unpack_question__()
        self._records = get_records(self._data_as_str)

    def send(self, sock, address):
        data_to_send = self.get_data_in_bytes()
        if data_to_send is not None:
            sock.sendto(data_to_send, address)

    def has_no_records(self):
        self.update_records()
        recs = self.get_records()
        return len(recs[0]) + len(recs[1]) + len(recs[2]) == 0

    def set_ID(self, id):
        self._data_as_str = id + self._data_as_str[byte_len*2:]
        self._data_in_bytes = convert_to_bytes(self._data_as_str)
        self._ID = id

    def __unpack_question__(self):
        body_as_str = self.get_body_as_str()

        qname, off = get_name(self._data_as_str)
        qtype = body_as_str[off: off + byte_len*2]
        qclass = body_as_str[off + byte_len*2: off + byte_len*4]

        self._question_as_str = body_as_str[:off + byte_len*4]

        return qname, qtype, qclass

    def get_all_info(self):
        return f"ID : {self._ID}\n" \
               f"flags : {self._flags}\n" \
               f"QDCOUNT : {self._QDCOUNT}\n" \
               f"ANCOUNT : {self._ANCOUNT}\n" \
               f"NSCOUNT : {self._NSCOUNT}\n" \
               f"ARCOUNT : {self._ARCOUNT}\n" \
               f"name : {self._qname}\n" \
               f"type : {self._qtype}\n" \
               f"class : {self._qclass}\n" \
               f"records: {''.join(self.get_records_as_str())}\n"

    def get_records_as_str(self):
        s = ""
        for record_list in self._records:
            for (record, name) in record_list:
                s += f"\n    name : {name}, " \
                     f"msg_type : {record.msg_type}, " \
                     f"class : 0001, ttl : {record.ttl}, " \
                     f"length : {record.get_length()}, " \
                     f"data : {record.get_data()}"
        return s

    def update_records(self):
        records = []
        for i in range(3):
            records_to_delete = []
            for j in range(len(self._records[i])):
                record, name = self._records[i][j]
                record_as_str = record.stringify()
                if record.ttl > int(round(time())):
                    records.append(record_as_str)
                else:
                    records_to_delete.append(self._records[i][j])
            for rec in records_to_delete:
                self._records[i].remove(rec)
        self._data_as_str = self.get_header_as_str() + self._question_as_str + ''.join(records)
        self._data_in_bytes = convert_to_bytes(self._data_as_str)

    def get_data_as_str(self):
        return self._data_as_str

    def get_data_in_bytes(self):
        return self._data_in_bytes

    def get_header_as_str(self):
        return self._data_as_str[:24]

    def get_body_as_str(self):
        return self._data_as_str[24:]

    def get_ID(self):
        return self._ID

    def get_flags(self):
        return self._flags

    def get_QDCOUNT(self):
        return self._QDCOUNT

    def get_ANCOUNT(self):
        return self._ANCOUNT

    def get_NSCOUNT(self):
        return self._NSCOUNT

    def get_ARCOUNT(self):
        return self._ARCOUNT

    def get_name(self):
        return self._qname

    def get_type(self):
        return self._qtype

    def get_class(self):
        return self._qclass

    def get_records(self):
        return self._records


def convert_to_str(bytes):
    return binascii.hexlify(bytes).decode(encoding)


def convert_to_bytes(str):
    return binascii.unhexlify(str)


def get_records(data_as_str):
    header, body = data_as_str[:header_as_str_len], data_as_str[header_as_str_len:]
    name, offset = get_name(data_as_str)
    (ANCOUNT, NSCOUNT, ARCOUNT) = (
        get_bytes_as_int(header, pos, bytes_count=2) for pos in [12, 16, 20])
    resource_record = body[offset + byte_len * 4:]

    records = [[], [], []]
    for (i, value) in enumerate([ANCOUNT, NSCOUNT, ARCOUNT]):
        if value == 0:
            continue
        record_and_name = parse_record(value, data_as_str, resource_record)
        records[i] = record_and_name
        resource_record = get_next_record(resource_record)

    return records


def get_next_record(resource_record):
    data_len_start = 10 * byte_len
    data_len = get_bytes_as_int(resource_record, data_len_start, bytes_count=2)
    end_of_record = data_len_start + byte_len * 2 + data_len * byte_len
    return resource_record[end_of_record:]
