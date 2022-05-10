import binascii
import socket
import pickle

from DnsResponsePackage import DnsResponsePackage
from help_methods import *

byte_len = 2
header_len = 24


def dump_cache(cache):
    with open('cache', 'wb') as f:
        pickle.dump(cache, f)


def load_cache():
    try:
        with open('cache', 'rb+') as f:
            cache = pickle.load(f)
            return cache
    except FileNotFoundError:
        return {}


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
    cache[(package.get_name(), package.get_type())] = package


def get_from_cache(data, cache):
    header, other_data_before = data[:header_len], data[header_len:]
    name, _ = get_name(data)
    type = other_data_before[-8: -4]

    if (name, type) in cache:
        package: DnsResponsePackage = cache[(name, type)]
        return binascii.unhexlify(header[:4]) + package.get_data_in_bytes()[2:]
    return None


def update_cache(cache : dict):
    keys_to_delete = []
    for (key, value) in cache.items():
        value.update_records()
        recs = value.get_records()
        if len(recs[0]) + len(recs[1]) + len(recs[2]) == 0:
            keys_to_delete.append(key)
    for key in keys_to_delete:
        del cache[key]


def run():
    my_cache = load_cache()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('localhost', 53))
    print('Server launched on 127.0.0.1: 53')

    while True:
        update_cache(my_cache)
        try:
            process_request(sock, my_cache)
        except KeyboardInterrupt:
            user_answer = -1
            while user_answer != 'Y' and user_answer != 'N':
                print('Shut down server?[Y/N]')
                user_answer = str(input())
            if user_answer == 'N':
                continue
            if user_answer == 'Y':
                dump_cache(my_cache)
                exit(0)


if __name__ == '__main__':
    run()
