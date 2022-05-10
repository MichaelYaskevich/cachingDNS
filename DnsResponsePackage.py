import binascii
import struct
from help_methods import *


class DnsResponsePackage:
    def __init__(self, data_in_bytes):
        self._data_in_bytes = data_in_bytes
        header, body = data_in_bytes[:12], data_in_bytes[12:]
        self._header = header
        self._body = body
        unpacked_header = struct.unpack("2s2s2s2s2s2s", header)
        self._ID, self._flags, self._QDCOUNT, self._ANCOUNT, self._NSCOUNT, self._ARCOUNT = \
            [binascii.hexlify(x).decode("utf-8") for x in unpacked_header]
        (self._qname, self._qtype, self._qclass) = self.__unpack_question__()
        self._records = self.__get_records__(self._data_as_str)

    def __unpack_question__(self):
        self._data_as_str = binascii.hexlify(
            self._data_in_bytes).decode("utf-8")
        self._header_as_str = binascii.hexlify(
            self._header).decode("utf-8")
        self._body_as_str = binascii.hexlify(
            self._body).decode("utf-8")

        qname, offset = get_name(self._data_as_str)
        qtype = self._body_as_str[offset: offset + 4]
        qclass = self._body_as_str[offset + 4: offset + 8]

        return qname, qtype, qclass

    def __get_records__(self, data_as_str):
        header, body = data_as_str[:header_len], data_as_str[header_len:]
        name, offset = get_name(data_as_str)
        (ANCOUNT, NSCOUNT, ARCOUNT) = (
            get_bytes_as_int(header, pos, bytes_count=2) for pos in [12, 16, 20])
        resource_record = body[offset + 8:]

        records = [[], [], []]
        for (i, value) in enumerate([ANCOUNT, NSCOUNT, ARCOUNT]):
            if value == 0:
                continue
            record_and_name = parse_record(value, data_as_str, resource_record)
            records[i] = record_and_name
            resource_record = resource_record[24 + int(resource_record[20:24], 16) * 2:]

        return records

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

    def get_data_as_str(self):
        return self._data_as_str

    def get_data_in_bytes(self):
        return self._data_in_bytes

    def get_header_as_str(self):
        return self._header_as_str

    def get_body_as_str(self):
        return self._body_as_str

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
