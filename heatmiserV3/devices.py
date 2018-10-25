from .crc16 import CRC16
from .config import Config
from .connection import Connection
from .protocol_manager import ProtocolManager
import logging


class Device:
    def __init__(self, protocol_id :str, name :str, address :int):
        self.protocol_id = protocol_id
        self.name = name
        self.address = address


class Master:
    def __init__(self, address :int):
        self.logger = logging.getLogger(__name__)
        self.address = address
        self.conn = None
        self.logger.info("Created master")

    def connect_device(self, device):
        self.conn = Connection().connect_device(device)

    def connect_ip(self, ip, port):
        self.conn = Connection().connect_ip(ip, port)

    def close_connection(self):
        self.conn.close()

    def _send_write_command(self, device, cmd):
        self.logger.info("Writing request %s ", ProtocolManager.to_hex_str(cmd))
        bytes_sent = self.conn.write(cmd)
        self.logger.info("Request sent, bytes=%i", bytes_sent)
        response = self.conn.read(7)
        self.logger.info("Response: %s", ProtocolManager.to_hex_str(response))
        return response

    def _send_read_command(self, device, cmd):
        self.logger.info("Sending read request %s ", ProtocolManager.to_hex_str(cmd))
        bytes_sent = self.conn.write(cmd)
        response = self.conn.read(9)
        self.logger.info("Response: %s", ProtocolManager.to_hex_str(response))
        # TODO: parse initial header response and use that to get number of bytes to read
        response = self.conn.read(255)
        self.logger.info("Response: %s", ProtocolManager.to_hex_str(response))
        return response

    def send_request_all(self, device):
        cmd = self._build_command(device, False, Config.ALL_FIELDS_NAME)
        return self._send_read_command(device, cmd)

    def update_field(self, device: Device, field_name :str, data):
        if not isinstance(data,list):
            data = [data]
        cmd = self._build_command(device, True, field_name, data)
        return self._send_write_command(device, cmd)

    def _build_command(self, device :Device, is_write :bool, field_name :str, data :list=None ) -> list:
        if is_write:
            if not data:
                raise ValueError("Must have data if writing")
            if field_name == Config.ALL_FIELDS_NAME:
                raise ValueError("Can only write to one field at a time")

        length = len(data)+10 if is_write and data else 10

        if field_name == Config.ALL_FIELDS_NAME:
            start_address = 0
            read_write_length = Config.ALL_FIELDS_SIZE
        else:
            protocol = ProtocolManager().get_protocol(device.protocol_id)
            field = protocol.get_field(field_name)
            if not field:
                raise ValueError("Unhandled field not found in protocol.yml: " + field_name)
            start_address = field.offset
            read_write_length = field.get_length()

        msg = [
            device.address,
            length,
            self.address,
            1 if is_write else 0,
            start_address & Config.BYTEMASK,
            (start_address >> 8) & Config.BYTEMASK,
            read_write_length & Config.BYTEMASK,
            (read_write_length >> 8) & Config.BYTEMASK,
        ]
        if data:
            msg += data

        crc = CRC16()
        msg = msg + crc.run(msg)
        return msg


