import yaml
import sys
import serial

from .config import Config
from .crc16 import CRC16


class Heatmiser(object):

    """Initialises a heatmiser component, by taking an address and model."""
    def __init__(self, address, model, conn):
        self.address = address
        self.model = model
        self.conn = conn
        with open("heatmiserV3/config.yml", "r") as stream:
            try:
                config = yaml.load(stream)
                self.config = Config()['devices'][model]
            except yaml.YAMLError as exc:
                print("The YAML file is invalid: %s", exc)

    def _hm_form_message(
            self,
            destination,
            protocol,
            source,
            function,
            start,
            payload):

        """Forms a message payload, excluding CRC"""
        if protocol == config.HMV3_ID:
            start_low = (start & config.BYTEMASK)
            start_high = (start >> 8) & config.BYTEMASK
            if function == config.FUNC_READ:
                payload_length = 0
                length_low = (config.RW_LENGTH_ALL & config.BYTEMASK)
                length_high = (config.RW_LENGTH_ALL
                               >> 8) & config.BYTEMASK
            else:
                payload_length = len(payload)
                length_low = (payload_length & config.BYTEMASK)
                length_high = (payload_length >> 8) & config.BYTEMASK
            msg = [
                destination,
                10 + payload_length,
                source,
                function,
                start_low,
                start_high,
                length_low,
                length_high
            ]
            if function == config.FUNC_WRITE:
                msg = msg + payload
                type(msg)
            return msg
        else:
            assert 0, "Un-supported protocol found %s" % protocol

    def _hm_form_message_crc(
            self,
            destination,
            protocol,
            source,
            function,
            start,
            payload
    ):
        """Forms a message payload, including CRC"""
        data = self._hm_form_message(
            destination, protocol, source, function, start, payload)
        crc = CRC16()
        data = data + crc.run(data)
        return data

    def _hm_verify_message_crc_uk(
            self,
            destination,
            protocol,
            source,
            expectedFunction,
            expectedLength,
            datal
    ):
        """Verifies message appears legal"""
        # expectedLength only used for read msgs as always 7 for write
        badresponse = 0
        if protocol == config.HMV3_ID:
            checksum = datal[len(datal) - 2:]
            rxmsg = datal[:len(datal) - 2]
            crc = CRC16()   # Initialises the CRC
            expectedchecksum = crc.run(rxmsg)
            if expectedchecksum == checksum:
                print("CRC is correct")
            else:
                print("CRC is INCORRECT")
                serror = "Incorrect CRC"
                sys.stderr.write(serror)
                badresponse += 1
            dest_addr = datal[0]
            frame_len_l = datal[1]
            frame_len_h = datal[2]
            frame_len = (frame_len_h << 8) | frame_len_l
            source_addr = datal[3]
            func_code = datal[4]

            if (dest_addr != 129 and dest_addr != 160):
                print("dest_addr is ILLEGAL")
                serror = "Illegal Dest Addr: %s\n" % (dest_addr)
                sys.stderr.write(serror)
                badresponse += 1

            if dest_addr != destination:
                print("dest_addr is INCORRECT")
                serror = "Incorrect Dest Addr: %s\n" % (dest_addr)
                sys.stderr.write(serror)
                badresponse += 1

            if (source_addr < 1 or source_addr > 32):
                print("source_addr is ILLEGAL")
                serror = "Illegal Src Addr: %s\n" % (source_addr)
                sys.stderr.write(serror)
                badresponse += 1

            if source_addr != source:
                print("source addr is INCORRECT")
                serror = "Incorrect Src Addr: %s\n" % (source_addr)
                sys.stderr.write(serror)
                badresponse += 1

            if (
                func_code != config.FUNC_WRITE and
                    func_code != config.FUNC_READ
            ):
                print("Func Code is UNKNWON")
                serror = "Unknown Func Code: %s\n" % (func_code)
                sys.stderr.write(serror)
                badresponse += 1

            if func_code != expectedFunction:
                print("Func Code is UNEXPECTED")
                serror = "Unexpected Func Code: %s\n" % (func_code)
                sys.stderr.write(serror)
                badresponse += 1

            if (
                    func_code == config.FUNC_WRITE and
                    frame_len != 7
            ):
                # Reply to Write is always 7 long
                print("response length is INCORRECT")
                serror = "Incorrect length: %s\n" % (frame_len)
                sys.stderr.write(serror)
                badresponse += 1

            if len(datal) != frame_len:
                print("response length MISMATCHES header")
                serror = "Mismatch length: %s %s\n" % (len(datal), frame_len)
                sys.stderr.write(serror)
                badresponse += 1

            """if (func_code == constants.FUNC_READ and expectedLength !=len(datal) ):
              # Read response length is wrong
              print("response length not EXPECTED value")
              print(len(datal))
              print(datal)
              s = "Incorrect length: %s\n" % (frame_len)
              sys.stderr.write(s)
              badresponse += 1
            """
            if (badresponse == 0):
                return True
            else:
                return False

        else:
            assert 0, "Un-supported protocol found %s" % protocol

    def _hm_send_msg(self, message):
        """This is the only interface to the serial connection."""
        try:
            serial_message = message
            self.conn.write(serial_message)   # Write a string
        except serial.SerialTimeoutException:
            serror = "Write timeout error: \n"
            sys.stderr.write(serror)
        # Now wait for reply
        byteread = self.conn.read(159)
        # NB max return is 75 in 5/2 mode or 159 in 7day mode
        datal = list(byteread)
        return datal

    def _hm_send_address(self, destination, address, state, readwrite):
        protocol = config.HMV3_ID
        if protocol == config.HMV3_ID:
            payload = [state]
            msg = self._hm_form_message_crc(
                destination,
                protocol,
                config.RW_MASTER_ADDRESS,
                readwrite,
                address,
                payload
            )
        else:
            assert 0, "Un-supported protocol found %s" % protocol
        string = bytes(msg)
        datal = self._hm_send_msg(string)
        pro = protocol
        if readwrite == 1:
            verification = self._hm_verify_message_crc_uk(
                0x81, pro, destination, readwrite, 1, datal)
            if verification is False:
                print("OH DEAR BAD RESPONSE")
            return datal
        else:
            verification = self._hm_verify_message_crc_uk(
                0x81, pro, destination, readwrite, 75, datal)
            if verification is False:
                print("OH DEAR BAD RESPONSE")
            return datal

    def _hm_read_address(self):
        """Reads from the DCB and maps to yaml config file."""
        response = self._hm_send_address(self.address, 0, 0, 0)
        lookup = self.config['keys']
        offset = self.config['offset']
        keydata = {}
        for i in lookup:
            try:
                kdata = lookup[i]
                ddata = response[i + offset]
                keydata[i] = {
                    'label': kdata,
                    'value': ddata
                }
            except IndexError:
                print("Finished processing at %d", i)
        return keydata

    def get_dcb(self):
        """
        Returns the full DCB
        """
        return self._hm_read_address()