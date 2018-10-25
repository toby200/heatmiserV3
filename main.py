from datetime import time
import time as t

from heatmiserV3.devices import Master, Device
from heatmiserV3.config import Config
import logging
import logging.config

from heatmiserV3.protocol_manager import ProtocolManager


def main():
    log_config = Config.LOG_CONFIG
    logging.config.dictConfig(log_config)

    logger = logging.getLogger(__name__)

    master = Master(Config.MASTER_IRQ_ADDRESS)

    location = Config.MASTER_LOCATION['location']

    if Config.MASTER_LOCATION['type'].casefold() == 'ip'.casefold():
        master.connect_ip(location)
    elif Config.MASTER_LOCATION['type'].casefold() == 'device'.casefold():
        master.connect_device(location)
    else:
        raise ValueError("Unrecognized value for Config.MASTER_LOCATION.type, try ip or device",
     Config.MASTER_LOCATION[
            'type'])


    tm1 = Device("tm1", "Boat Timer", 0)
    protocol = ProtocolManager().get_protocol("tm1")

    # # sync time always
    # logger.info("Syncing time")
    # dow_time = ProtocolManager.get_dow_time()
    # response = master.update_field(tm1, "Current time", dow_time)
    # logger.info("Time synced, response={}".format(ProtocolManager().to_hex_str(response)))


    # t.sleep(1)
    # logger.info("Updating weekday schedule")
    # timer_block = ProtocolManager().get_timer_block(
    #     [[time(hour=5, minute=8), time(hour=11, minute=17)], [time(hour=19), time(hour=21, minute=9)]])
    # response = master.update_field(tm1, "Weekday", timer_block)
    # logger.info("Updated weekday schedule, response={}".format(ProtocolManager().to_hex_str(response)))
    # #

    t.sleep(1)

    # master.update_field(tm1, "On/Off", 1)
    #master.update_field(tm1, "Current timer state", 2) #1=on 2=off
    #
    response = master.send_request_all(tm1)
    parsed_response = protocol.parse_response(response)
    print("parsed response:")
    for k, v in sorted(parsed_response.items()):
        print(k, v)

    master.close_connection()

if __name__ == '__main__':
    main()
