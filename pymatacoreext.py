import time

import asyncio

from pymata_aio.pymata3 import PyMata3
from pymata_aio.pymata_core import PymataCore


class ExtConstants:
    DHT_CONFIG = 0x66  # configure DHT
    DHT_DATA = 0x67  # DHT data returned

    # DHT sensor type
    DHT_TYPE_DHT11 = 11
    DHT_TYPE_DHT22 = 22
    DHT_TYPE_DHT21 = 21
    DHT_TYPE_AM2301 = 21


class ExtPyMataCore(PymataCore):
    def __init__(self, arduino_wait=2, sleep_tune=0.0001, log_output=False, com_port=None, ip_address=None,
                 ip_port=2000, ip_handshake='*HELLO*'):
        super().__init__(arduino_wait, sleep_tune, log_output, com_port, ip_address, ip_port, ip_handshake)

    async def dht_config(self, dht_type, dht_pin):
        """
        """
        await self._send_sysex(ExtConstants.DHT_CONFIG, [dht_type, dht_pin])

    async def dht_get_data(self, dht_pin):
        """
        This method retrieves DHT data

        :arg dht_pin:
        :returns: DHT Data
        """
        current_time = time.time()
        if self.query_reply_data.get(ExtConstants.DHT_DATA) == '':
            await self._send_sysex(ExtConstants.DHT_DATA, [dht_pin])
            while self.query_reply_data.get(ExtConstants.DHT_DATA) == '':
                elapsed_time = time.time()
                if elapsed_time - current_time > 2:
                    return None
                await asyncio.sleep(self.sleep_tune)
        reply = ''
        for x in self.query_reply_data.get(ExtConstants.DHT_DATA):
            reply_data = ord(x)
            if reply_data:
                reply += chr(reply_data)
        self.query_reply_data[ExtConstants.DHT_DATA] = reply
        return self.query_reply_data.get(ExtConstants.DHT_DATA)

    def _dht_data(self, data):
        """
        This method handles the incoming DHT data message and stores the data in the response table.

        :param data: Message data from Firmata
        :returns: No return value.
        """
        # strip off sysex start and end
        data = data[1:-1]
        print(data)

    def extended_command_dictionary(self):
        return {ExtConstants.DHT_DATA: self._dht_data}


class ExtPyMata3(PyMata3):
    def __init__(self, arduino_wait=2, sleep_tune=0.0001, log_output=False, com_port=None, ip_address=None,
                 ip_port=2000, ip_handshake='*HELLO*', pymata_core_impl=PymataCore):
        super().__init__(arduino_wait, sleep_tune, log_output, com_port, ip_address, ip_port, ip_handshake,
                         pymata_core_impl)
