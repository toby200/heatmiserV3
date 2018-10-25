from heatmiserV3.config import Config
from heatmiserV3.devices import Device, Master

import unittest

class TestLive(unittest.TestCase):

    def test_request_all(self):
        master = Master(Config.MASTER_IRQ_ADDRESS)

        location = Config.MASTER_LOCATION['location']

        if Config.MASTER_LOCATION['type'].casefold() == 'ip'.casefold():
            master.connect_ip(location)
        elif Config.MASTER_LOCATION['type'].casefold() == 'device'.casefold():
            master.connect_device(location)
        else:
            raise ValueError("Unrecognized value for Config.MASTER_LOCATION.type, try ip or device", Config.MASTER_LOCATION[
                'type'])

        # for i in range(0,33):
        i = 0
        print("Testing ", i)
        tm1 = Device("tm1", "Boat Timer", i)
        master.send_request_all(tm1)

        master.close_connection()