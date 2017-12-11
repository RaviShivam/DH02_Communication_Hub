import json
import paho.mqtt.client as mqtt
import RPi.GPIO as gpio
from random import random
from mission_configs import *
# from messenger_ch import hercules_messenger
from messenger_ch import hercules_messenger
from messenger_ch import mc_messenger
from messenger_ch import udp_messenger
from messenger_ch import mission_logger
import itertools
import time

# Initialize log
low_frequency_logger = mission_logger(LOW_FREQUENCY_LOG_FILE)
high_frequency_logger = mission_logger(HIGH_FREQUENCY_LOG_FILE)

# Initialize hercules communication module
low_frequency_module = hercules_comm_module()

# Initialize all messengers
client = mqtt.Client(MQTT_CLIENT_NAME)
hercules_messenger = hercules_messenger(SENDING_FREQUENCY_HERCULES)
mc_messenger = mc_messenger(client, HEARTBEAT_TIMEOUT_MC, sending_frequency=SENDING_FREQUENCY_MC)
spacex_messenger = udp_messenger(client, sending_frequency=SENDING_FREQUENCY_SPACEX)

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
        retrieved_data = hercules_messenger.retrieve_data()
        if mc_messenger.is_mc_alive():
            mc_messenger.send_data(json.dumps())
        else:
            mc_messenger.TRIGGER_EMERGENCY_BRAKE()
            try_to_reconnect()
except KeyboardInterrupt:
    gpio.output(BRAKE_PIN, False)
    gpio.cleanup()
