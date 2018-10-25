from heatmiserV3.protocol_manager import ProtocolManager
from datetime import time

import unittest


class TestProtocolManager(unittest.TestCase):

    def test_field_lookup(self):
        print("***Testing field lookups***")
        self._field_lookup("Current timer state", 42)
        self._field_lookup("On/Off", 21)

        self._field_lookup("Current time", 43, 4)
        self._field_lookup("Weekday", 71, 16)

    @staticmethod
    def _field_lookup(field_name, expected_offset, expected_length=1):
        protocol = ProtocolManager().get_protocol("tm1")
        field = protocol.get_field(field_name)

        assert field is not None, "No field returned for {}".format(field_name)
        assert field.offset == expected_offset, ("Expected {} field offset of {} not {}".format(
               field_name, expected_offset, field.offset))
        assert field.get_length() == expected_length, "Expected {}  field length of {} not {}".format(
                field_name, expected_length, field.get_length())


    def test_parse_response(self):
        print("***Testing response parsing***")
        protocol = ProtocolManager().get_protocol("tm1")
        dcb = protocol.parse_response(
            b'\x00\x33\x00\x11\x05\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x15\x2b\x0c\x07\x00\x09\x00\x10\x00'
        + b'\x14\x00\x18\x00\x18\x00\x18\x00\x18\x00\x07\x00\x09\x00\x10\x00\x14\x00\x18\x00\x18\x00\x18\x00\x18\x00'
        + b'\xca\x0b'
        )
        print('Parsed model:')
        for k, v in sorted(dcb.items()):
            print(k, v)

        assert dcb['Current time'] == {'day of week': 1, 'hour': 21, 'minute': 43, 'seconds': 12}, \
            "Invalid current time"
        assert dcb['Current timer state'] == 0, "timer should be off"
        assert dcb['On/Off'] == 0, "unit should be off"
        assert dcb['Weekday']['Period 1'] == \
               {'On Time': {'hour': 7, 'minute': 0}, 'Off Time': {'hour': 9, 'minute': 0}}, \
            "Invalid Weekday period 1 - should be from 7 til 9"

    def test_get_period(self):
        print("***Testing period conversion***")
        start = time(hour=5, minute=30)
        end = time(hour=6, minute=10)
        period = ProtocolManager().get_period(start, end)
        expected = [5, 30, 6, 10]
        assert period == expected, "Period {} doesn't match expected {}".format(period, expected)

    def test_get_timer_block(self):
        print("***Testing timer_block conversion***")

        start = time(hour=5, minute=30)
        end = time(hour=6, minute=10)
        periods = [[start, end]]
        timer_block = ProtocolManager().get_timer_block(periods)
        print(timer_block)

