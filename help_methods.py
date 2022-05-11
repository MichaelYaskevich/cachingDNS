from record import Record

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


def get_part_name(data, label_length, name):
    start_from = int(bin(label_length)[2:], 2) * 2
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


def parse_record(count, data, section):
    result = []
    for i in range(count):
        start_of_name = int(section[2:4], 16) * byte_len
        name, _ = get_name(data[start_of_name:], 0)

        ttl = section[12:20]
        msg_type = section[4:8]

        end_of_section = 24 + int(section[20:24], 16) * 2
        record_data = section[24:end_of_section]
        section = section[end_of_section:]
        result.append((Record(record_data, msg_type, ttl), name))
    return result