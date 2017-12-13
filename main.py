import json
import time

import RPi.GPIO as gpio
import paho.mqtt.client as mqtt

from messenger_ch import hercules_comm_module
from messenger_ch import hercules_messenger
from messenger_ch import mc_messenger
from messenger_ch import mission_logger
from messenger_ch import udp_messenger
from messenger_ch import data_segmentor
from mission_configs import *

initialize_GPIO()

# Initialize hercules communication module
low_frequency_retriever = hercules_comm_module(LOW_FREQUENCY_RETRIEVAL_SPEED, LOW_FREQUENCY_REQUEST_PACKET, CHIP_SELECT_LOW_FREQUENCY)
high_frequency_retriever = hercules_comm_module(HIGH_FREQUENCY_RETRIEVAL_SPEED, HIGH_FREQUENCY_REQUEST_PACKET, CHIP_SELECT_HIGH_FREQUENCY)

# Initialize all messengers
client = mqtt.Client(MQTT_CLIENT_NAME)
mc_messenger = mc_messenger(client, HEARTBEAT_TIMEOUT_MC, SENDING_FREQUENCY_MC)
hercules_messenger = hercules_messenger([low_frequency_retriever, high_frequency_retriever], CHIP_SELECT_COMMAND)
spacex_messenger = udp_messenger(sending_frequency=SENDING_FREQUENCY_SPACEX)

# Initialize log
# low_frequency_logger = mission_logger(LOW_FREQUENCY_LOG_FILE)
# high_frequency_logger = mission_logger(HIGH_FREQUENCY_LOG_FILE)

run = True


def handle_received_commands():
    while not mc_messenger.COMMAND_BUFFER.empty():
        command, args = mc_messenger.COMMAND_BUFFER.get()
        hercules_messenger.send_command(command, args)

try:
    while run:
        handle_received_commands()
        retrieved_data = hercules_messenger.retrieve_data()
        # low_frequency_logger.log_data(low_frequency_logger)
        # high_frequency_logger.log_data(high_frequency_logger)
        # spacex_messenger.send_data(retrieved_data)
        if mc_messenger.is_mc_alive():
            mc_messenger.send_data(data_segmentor().segment_mc_data(retrieved_data))
        else:
            mc_messenger.try_to_reconnect()
except KeyboardInterrupt:
    gpio.output(BRAKE_PIN, False)
    gpio.cleanup()
