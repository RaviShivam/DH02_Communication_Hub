import json
import paho.mqtt.client as mqtt
import RPi.GPIO as gpio
from random import random
from mission_configs import *
# from messenger_ch import hercules_messenger
from messenger_ch import hercules_messenger
from messenger_ch import mc_messenger
from messenger_ch import udp_messenger
from messenger_ch import logging_messenger
import itertools
import time

client = mqtt.Client(MQTT_CLIENT_NAME)
hercules_messenger = hercules_messenger(SENDING_FREQUENCY_HERCULES)
mc_messenger = mc_messenger(client, hercules_messenger, HEARTBEAT_TIMEOUT_MC, sending_frequency=SENDING_FREQUENCY_MC)
spacex_messenger = udp_messenger(client, sending_frequency=SENDING_FREQUENCY_SPACEX)
pi_logger = logging_messenger(logging_frequency=LOGGING_FREQUENCY)

run = True
def try_to_reconnect():
    while True:
        print("Trying to reconnect")
        time.sleep(0.5)
        if mc_messenger.is_mc_alive():
            break
    gpio.output(BRAKE_PIN, True)

try:
    while run:
        status = hercules_messenger.get_pod_status()
        # data = hercules_messenger.get_data()
        pi_logger.log_data(data=status)
        if mc_messenger.is_mc_alive():
            mc_messenger.send_data(json.dumps(status))
        else:
            hercules_messenger.BRAKE()
            try_to_reconnect()
except KeyboardInterrupt:
    gpio.output(BRAKE_PIN, False)
    gpio.cleanup()
