from heatmiserV3.config import Config
from heatmiserV3.devices import Device, Master

import unittest

class TestDevices(unittest.TestCase):

    def test_request_all(self):
        tm1 = Device("tm1", "Boat Timer", 1)
        master = Master(0x81)

        msg = master.build_command(tm1, False, Config.ALL_FIELDS_NAME)
        byte_msg = bytes(msg)
        expected = b'\x01\x0a\x81\x00\x00\x00\xff\xff\x2c\x09' # includes 2 crc bytes

        print()
        print("generated=", str(byte_msg),"\t\t",  " ".join("{:02x}".format(x) for x in byte_msg))
        print("expected =", str(expected), "\t\t", " ".join("{:02x}".format(x) for x in expected))


        assert(byte_msg == expected)

    def test_full_response(self):


        response = b'3\x00\x11\x05\xfd\xeb\xfd\xff\xff\xff'
