import paho.mqtt.client as mqtt
from mission_configs import *
# from messenger_ch import hercules_messenger
from messenger_ch import dummy_hercules
from messenger_ch import mc_messenger
from messenger_ch import udp_messenger
from messenger_ch import logging_messenger
import json

client = mqtt.Client(MQTT_CLIENT_NAME)
hercules_messenger = dummy_hercules()
mc_messenger = mc_messenger(client, None, HEARTBEAT_TIMEOUT_MC, sending_frequency=SENDING_FREQUENCY_MC)
spacex_messenger = udp_messenger(client, sending_frequency=SENDING_FREQUENCY_SPACEX)
pi_logger = logging_messenger(client, logging_frequency=LOGGING_FREQUENCY)

run = True
pod_status = 1

while run:
    if mc_messenger.check_mc_alive():
        mc_messenger.send_data(json.dumps(pod_status))
    else:
        if pod_status is 1:
            dummy_hercules.BRAKE()
        else:
            print("Trying to reconnect")


    # TODO: logger.log(data)
    # TODO: spacex_messenger.send_data(data)
