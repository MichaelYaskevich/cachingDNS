import binascii
import socket
import pickle

from DnsResponsePackage import DnsResponsePackage
from help_methods import *

byte_len = 2
header_len = 24
port = 53
server = "8.8.8.8"
bufsize = 4096
encoding = "utf-8"


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
    data, addr = sock.recvfrom(bufsize)
    data = binascii.hexlify(data).decode(encoding)
    resp_package = get_from_cache(data, cache)

    if resp_package is None:
        print('From server')

        data = data.replace("\n", "").replace(" ", "")
        resp_package = get_response_from_server(data)
        cache_records(resp_package, cache)
    else:
        print('From cash')

    if resp_package is not None:
        save_parsed_response(resp_package)
        resp_package.send(sock, addr)


def get_response_from_server(data):
    with socket.socket(
            socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.settimeout(2)
        try:
            s.sendto(binascii.unhexlify(data), (server, port))
            response_from_server, _ = s.recvfrom(bufsize)
        except socket.timeout:
            print(f"Can't reach server {server} while recursive request")
        else:
            if response_from_server is not None:
                return DnsResponsePackage(response_from_server)


def save_parsed_response(package: DnsResponsePackage):
    with open("parsed_responses.txt", 'a') as f:
        f.write(package.get_all_info())
        f.write('--------------------------------------')


def cache_records(package, cache):
    cache[(package.get_name(), package.get_type())] = package


def get_from_cache(data, cache):
    header, body = data[:header_len], data[header_len:]
    name, _ = get_name(data)
    type = body[-byte_len*4: -byte_len*2]

    if (name, type) in cache:
        package: DnsResponsePackage = cache[(name, type)]
        package.set_ID(header[:byte_len*2])
        return package
    return None


def update_cache(cache: dict):
    keys_to_delete = []

    for (key, resp_package) in cache.items():
        if resp_package.has_no_records():
            keys_to_delete.append(key)

    for key in keys_to_delete:
        del cache[key]


def clear_parsed_responses_file():
    with open("parsed_responses.txt", 'w') as f:
        f.write('')


def run():
    clear_parsed_responses_file()
    cache = load_cache()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('localhost', port))
    print('Server launched on 127.0.0.1: 53')

    while True:
        update_cache(cache)
        try:
            process_request(sock, cache)
        except KeyboardInterrupt:
            user_answer = -1
            while user_answer != 'Y' and user_answer != 'N':
                user_answer = str(input('Shut down server?[Y/N]'))
            if user_answer == 'N':
                continue
            if user_answer == 'Y':
                dump_cache(cache)
                exit(0)


if __name__ == '__main__':
    run()
