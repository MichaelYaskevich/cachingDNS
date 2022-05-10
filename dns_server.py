import binascii
import socket
import pickle

from DnsResponsePackage import DnsResponsePackage
from help_methods import *

byte_len = 2
header_len = 24
my_cache = {}


def process_request(sock, cache):
    data, addr = sock.recvfrom(4096)
    data = binascii.hexlify(data).decode("utf-8")
    name, _ = get_name(data)
    cached_result = get_from_cache(data, cache)

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
                package = DnsResponsePackage(response_from_server)
                with open("parsed_responses.txt", 'a') as f:
                    f.write(package.get_all_info())
                    f.write('--------------------------------------')
                cache_records(package, cache)
                result = response_from_server
    else:
        print('From cash')
        result = cached_result
    if result is not None:
        sock.sendto(result, addr)


def cache_records(package, cache):
    cache[(package.get_name(), package.get_type())] = package.get_data_in_bytes()


def get_from_cache(data, cache):
    header, other_data_before = data[:header_len], data[header_len:]
    name, _ = get_name(data)
    type = other_data_before[-8: -4]

    if (name, type) in cache:
        return binascii.unhexlify(header[:4]) + cache[(name, type)][2:]
    return None


def run():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('localhost', 53))
    print('Server launched on 127.0.0.1: 53')

    while True:
        try:
            process_request(sock, my_cache)
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
