import yaml

from heatmiserV3.singleton import Singleton


class Structures(metaclass=Singleton):

    def __init__(self):
        cfg = self._load_protocol_cfg()
        self.structures = cfg['structures']

    @staticmethod
    def _load_protocol_cfg():
        with open("config/protocol.yml", "r") as stream:
            return yaml.load(stream)