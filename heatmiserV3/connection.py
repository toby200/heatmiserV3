"""This module is effectively a singleton for serial comms"""
import sys
import serial
from heatmiserV3.singleton import Singleton
from heatmiserV3.config import Config


class Connection(metaclass=Singleton):

    def __init__(self):
        self.connection = None

    def connect_device(self, device):
        """Connect using a serial device on /dev, eg /dev/serial0
        NB: Pi Zero W uses /dev/ttyAMA0 for bluetooth controller"""

        if self.connection is not None and self.connection.is_open:
            return self.connection

        config = Config().SERIAL_CONFIG
        try:
            self.connection = serial.Serial(port=device,
                          baudrate=config['baud'],
                          bytesize=config['size'],
                          parity=config['parity'],
                          stopbits=config['stop'],
                          timeout=config['timeout'],
                          write_timeout=config['timeout'])
        except serial.SerialException as e_message:
            s_message = "Could not open serial port %s: %s\n" % (
                self.connection.portstr,
                e_message)
            sys.stderr.write(s_message)
            self.connection.close()

        if not self.connection:
            sys.stderr.write("Failed to connect to serial port ", device)
        return self.connection

    def connect_ip(self, ipaddress, port):
        """Connect using an ip address and port; this works if you're using some ethernet to RS"""
        if self.connection is not None and self.connection.is_open:
            return self.connection

        config = Config().SERIAL_CONFIG
        try:
            self.connection = serial.serial_for_url(
                url="socket://" + ipaddress + ":" + port,
                baudrate=config['baud'],
                bytesize=config['size'],
                parity=config['parity'],
                stopbits=config['stop'],
                timeout=config['timeout'])
        except serial.SerialException as e_message:
            s_message = "Could not open serial port %s: %s\n" % (
                self.connection.portstr,
                e_message
            )
            sys.stderr.write(s_message)
            self.connection.close()

        return self.connection

    def reset(self):
        if self.connection is not None:
            try:
                self.connection.close()
            finally:
                self.connection = None

