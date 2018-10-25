from datetime import datetime, time

import yaml

from heatmiserV3.protocol import Protocol
from heatmiserV3.singleton import Singleton


class ProtocolManager(metaclass=Singleton):

    def __init__(self):
        cfg = self._load_protocol_cfg()
        self.protocols = self._load_protocols(cfg)

    @staticmethod
    def _load_protocol_cfg():
        with open("config/protocol.yml", "r") as stream:
            return yaml.load(stream)

    @staticmethod
    def _load_protocols(protocol_cfg):
        protocols = {}

        for device_id, protocol_cfg in protocol_cfg['protocols'].items():
            protocol = Protocol(device_id, protocol_cfg)
            protocols[device_id] = protocol

        return protocols

    def get_protocol(self, protocol):
        return self.protocols[protocol]

    @staticmethod
    def get_dow_time():
        now = datetime.now()
        return [now.isoweekday(),now.hour,now.minute,now.second]

    @staticmethod
    def get_2_byte(value :int) -> bytes:
        return value.to_bytes(2, 'little')

    @staticmethod
    def get_period(start_time :time, end_time :time) -> list:
        # hour=24 is used by heatmiser to indicate no action
        return [start_time.hour if start_time else 24,
                      start_time.minute if start_time else 0,
                      end_time.hour if end_time else 24,
                      end_time.minute if end_time else 0]

    @staticmethod
    def get_timer_block(periods :list) -> list:
        """Takes a list of up to 4 sub lists; each sublist is up to 2 datetime.time entries for start and optionally
        stop time."""
        timer_block = []
        if len(periods) > 4:
            raise ValueError("Cannot have more than 4 periods specified in one timer block")
        while len(periods) < 4:
            periods.append([None, None]) # fill up with blanks so there's the 4 required periods
        for period in periods:
            if len(period) == 1:
                period.append(None) # No stop time
            if len(period) != 2:
                raise ValueError("Must have 1 or 2 times per period - 1st for start and 2nd for stop")
            timer_block += ProtocolManager().get_period(period[0], period[1])
        return timer_block

    @staticmethod
    def to_hex_str(value :list):
        return " ".join("{:02x}".format(x) for x in value)


