import binascii
import socket
from time import time
import pickle

from record import Record
from help_methods import *

byte_len = 2
header_len = 24
my_cache = {}


def proccess_request(sock, cache):
    data, addr = sock.recvfrom(4096)
    data = binascii.hexlify(data).decode("utf-8")
    name, _ = get_name(data)

    cached_result = get_from_cache(data, cache)
    if cached_result is not None:
        cached_result = binascii.unhexlify(cached_result)

    if cached_result is None:
        print('From server')
        data = data.replace("\n", "").replace(" ", "")
        with socket.socket(
                socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.settimeout(2)
            try:
                s.sendto(binascii.unhexlify(data), ("8.8.8.8", 53))
                response_from_server, _ = s.recvfrom(4096)
            except:
                result = None
            else:
                data2 = binascii.hexlify(
                    response_from_server).decode("utf-8")
                records = get_records(data2)
                cache_records(records, cache)
                result = response_from_server
    else:
        print('From cash')
        result = cached_result
    if result is not None:
        sock.sendto(result, addr)


def get_records(data):
    header, body = data[:header_len], data[header_len:]
    name, offset = get_name(data)
    (ANCOUNT, NSCOUNT, ARCOUNT) = (
        get_bytes_as_int(header, pos, bytes_count=2) for pos in [12, 16, 20])
    resource_record = body[offset + 8:]

    records = [[], [], []]
    for (i, value) in enumerate([ANCOUNT, NSCOUNT, ARCOUNT]):
        if value == 0:
            continue
        record_and_name = parse_record(value, data, resource_record)
        records[i] = record_and_name
        resource_record = resource_record[24 + int(resource_record[20:24], 16) * 2:]

    return records


def cache_records(records: dict, cache):
    for record_and_name in records:
        for record, name in record_and_name:
            if (name, record.msg_type) not in cache:
                cache[(name, record.msg_type)] = record_and_name


def parse_record(count, data, section):
    result = []
    for i in range(count):
        start_of_name = int(section[2:4], 16) * byte_len
        name, _ = get_name(data[start_of_name:], 0)

        ttl = section[12:20]
        msg_type = section[4:8]

        record_data = section[24:24 + int(section[20:24], 16) * 2]
        result.append((Record(record_data, msg_type, ttl), name))
    return result


def get_from_cache(data, cache):
    header, other_data_before = data[:header_len], data[header_len:]
    name, _ = get_name(data)
    qtype = other_data_before[-8: -4]

    if (name, qtype) in cache.keys():
        records = []
        for (record, name) in cache[(name, qtype)]:
            format_answer = record.stringify()
            if record.ttl > int(round(time())):
                records.append(format_answer)
        count = len(records)

        if count != 0:
            return (header[:4] + "8180" + header[8:12] + hex(count)[2:].rjust(4, '0')
                    + header[16:] + other_data_before + ''.join(records))
    return None


def run():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('localhost', 53))
    print('Server launched on 127.0.0.1: 53')

    while True:
        try:
            proccess_request(sock, my_cache)
        except KeyboardInterrupt:
            user_answer = -1
            while user_answer != 'Y' and user_answer != 'N':
                user_answer = str(input('Shut down server?[Y/N]'))
            if user_answer == 'N':
                continue
            if user_answer == 'Y':
                exit(0)


if __name__ == '__main__':
    run()
