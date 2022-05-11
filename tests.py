import unittest
from dns_server import *


class Test(unittest.TestCase):
    def test_ya_ru_A(self):
        response = b'\x00\x11\x81\x80\x00\x01\x00\x01\x00\x00\x00\x00\x02\x79\x61\x02\x72\x75\x00\x00\x01\x00\x01\xc0\x0c\x00\x01\x00\x01\x00\x00\x01\x8d\x00\x04\x57\xfa\xfa\xf2'

        package = DnsResponsePackage(response)

        assert package.get_ID() == '0011'
        assert package.get_flags() == '8180'
        assert package.get_QDCOUNT() == '0001'
        assert package.get_ANCOUNT() == '0001'
        assert package.get_NSCOUNT() == '0000'
        assert package.get_ARCOUNT() == '0000'

        assert package.get_name() == 'ya.ru.'
        assert package.get_type() == '0001'
        assert package.get_class() == '0001'

        recs = package.get_records()
        assert len(recs) == 3
        assert len(recs[0]) == 1
        (record, name) = recs[0][0]
        assert name == 'ya.ru.'
        assert record.get_length() == '0004'
        assert record.get_data() == '57fafaf2'
        assert record.msg_type == '0001'

    def test_ya_ru_AAAA(self):
        response = b"\x00\x4a\x81\x80\x00\x01\x00\x01\x00\x00\x00\x00\x02\x79\x61\x02\x72\x75\x00\x00\x1c\x00\x01\xc0\x0c\x00\x1c\x00\x01\x00\x00\x00\xb0\x00\x10\x2a\x02\x06\xb8\x00\x00\x00\x00\x00\x00\x00\x00\x00\x02\x02\x42"

        package = DnsResponsePackage(response)

        assert package.get_ID() == '004a'
        assert package.get_flags() == '8180'
        assert package.get_QDCOUNT() == '0001'
        assert package.get_ANCOUNT() == '0001'
        assert package.get_NSCOUNT() == '0000'
        assert package.get_ARCOUNT() == '0000'

        assert package.get_name() == 'ya.ru.'
        assert package.get_type() == '001c'
        assert package.get_class() == '0001'

        recs = package.get_records()
        assert len(recs) == 3
        assert len(recs[0]) == 1
        (record, name) = recs[0][0]
        assert name == 'ya.ru.'
        assert record.get_length() == '0010'
        assert record.get_data() == '2a0206b8000000000000000000020242'
        assert record.msg_type == '001c'

    def test_vk_com_A(self):
        response = b"\x00\x4b\x81\x80\x00\x01\x00\x06\x00\x00\x00\x00\x02\x76\x6b\x03\x63\x6f\x6d\x00\x00\x01\x00\x01\xc0\x0c\x00\x01\x00\x01\x00\x00\x03\x40\x00\x04\x5d\xba\xe1\xd0\xc0\x0c\x00\x01\x00\x01\x00\x00\x03\x40\x00\x04\x57\xf0\x8b\xc2\xc0\x0c\x00\x01\x00\x01\x00\x00\x03\x40\x00\x04\x57\xf0\x89\x9e\xc0\x0c\x00\x01\x00\x01\x00\x00\x03\x40\x00\x04\x57\xf0\xbe\x43\xc0\x0c\x00\x01\x00\x01\x00\x00\x03\x40\x00\x04\x57\xf0\xbe\x48\xc0\x0c\x00\x01\x00\x01\x00\x00\x03\x40\x00\x04\x57\xf0\xbe\x4e"

        package = DnsResponsePackage(response)

        assert package.get_ID() == '004b'
        assert package.get_flags() == '8180'
        assert package.get_QDCOUNT() == '0001'
        assert package.get_ANCOUNT() == '0006'
        assert package.get_NSCOUNT() == '0000'
        assert package.get_ARCOUNT() == '0000'

        assert package.get_name() == 'vk.com.'
        assert package.get_type() == '0001'
        assert package.get_class() == '0001'

        recs = package.get_records()
        assert len(recs) == 3
        assert len(recs[0]) == 6
        assert len(recs[1]) == 0
        assert len(recs[2]) == 0
        (record, name) = recs[0][0]
        assert name == 'vk.com.'
        assert record.get_length() == '0004'
        assert record.get_data() == '5dbae1d0'
        assert record.msg_type == '0001'

        for (record, name) in recs[0]:
            assert name == 'vk.com.'
            assert record.get_length() == '0004'
            assert record.msg_type == '0001'

        record, _ = recs[0][0]
        l = record.get_length()
        assert record.get_data() == '5dbae1d0'

        record, _ = recs[0][1]
        assert record.get_data() == '57f08bc2'

        record, _ = recs[0][2]
        assert record.get_data() == '57f0899e'

        record, _ = recs[0][3]
        assert record.get_data() == '57f0be43'

        record, _ = recs[0][4]
        assert record.get_data() == '57f0be48'

        record, _ = recs[0][5]
        assert record.get_data() == '57f0be4e'

