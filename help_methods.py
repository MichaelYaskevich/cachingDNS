byte_len = 2
header_len = 24


def get_bytes_as_int(data, position, bytes_count):
    return int(data[position:position + bytes_count * byte_len], 16)


def get_name(data, start_from=24):
    name = ''
    offset = 0

    while True:
        position = start_from + offset
        label_length = get_bytes_as_int(data, position, bytes_count=1)

        if label_length >= 49152:
            name, offset = get_part_name(data, label_length, name)
            break

        if label_length == 0:
            offset += byte_len
            break

        name = add_part_name(data, name, position)
        offset += label_length * byte_len + byte_len

    return name, offset


def get_part_name(data, chunks, name):
    start_from = int(bin(chunks)[2:], 2) * 2
    part_name, offset = get_name(data, start_from)
    if name == "":
        name += part_name
    else:
        name += '.' + part_name
    return name, offset


def add_part_name(data, name, index):
    label_length = get_bytes_as_int(data, index, bytes_count=1)

    for i in range(byte_len, label_length * byte_len + byte_len, byte_len):
        name += chr(get_bytes_as_int(data, index + i, bytes_count=1))
    return name + "."