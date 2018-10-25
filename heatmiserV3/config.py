#
# Neil Trimboy 2011
#
from heatmiserV3.singleton import Singleton
import serial
import yaml

# Protocol for each controller
HMV2_ID = 2
HMV3_ID = 3

# Constants for Methods
# Passed to hmVerifyMsgCRCOK when message is of type FUNC_WRITE
DONT_CARE_LENGTH = 1

#
# HM Version 3 Magic Numbers
#

# Master must be in range [0x81,0xa0] = [129,160]
MASTER_ADDR_MIN = 0x81
MASTER_ADDR_MAX = 0xa0

# Define magic numbers used in messages
FUNC_READ = 0
FUNC_WRITE = 1

BROADCAST_ADDR = 0xff
RW_LENGTH_ALL = 0xffff


class Config(metaclass=Singleton):
    LOG_CONFIG = yaml.load(open('config/logging.yaml', 'r'))

    MASTER_LOCATION = {
        'type': 'device',           # or 'ip'
        'location': '/dev/serial0'  # or ip:port
    }

    # for linux tty types verify irq using dmesg | grep tty
    MASTER_IRQ_ADDRESS = 0xa0


    READ_WRITE = {
        'read': 0,
        'write': 1
    }

    SERIAL_CONFIG = {
        'baud': 4800,
        'size': serial.EIGHTBITS,
        'parity': serial.PARITY_NONE,
        'stop': serial.STOPBITS_ONE,
        'timeout': 2
    }

    DEVICES = {
        'name': 'Boat Timer',
        'type': 'tm1',
        'address': 0
    }

    #PROTOCOLS =
    BASIC_FIELD = 'basic'
    LENGTH = 'length'
    NAME = 'name'
    TYPE = 'type'

    ALL_FIELDS_NAME = "ALL"
    ALL_FIELDS_SIZE = 0xffff
    BYTEMASK = 0xff


