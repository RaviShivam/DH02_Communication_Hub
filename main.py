import json
import time

import RPi.GPIO as gpio
import messenger_ch.hercules_translator as ht
import paho.mqtt.client as mqtt

from messenger_ch import hercules_comm_module
from messenger_ch import hercules_messenger
from messenger_ch import mc_messenger
from messenger_ch import mission_logger
from messenger_ch import udp_messenger
from mission_configs import *

# Initialize hercules communication module
low_frequency_retriever = hercules_comm_module(LOW_FREQUENCY_RETRIEVAL_SPEED, LOW_FREQUENCY_REQUEST_PACKET,
                                               LOW_FREQUENCY_PIN)
high_frequency_retriever = hercules_comm_module(HIGH_FREQUENCY_RETRIEVAL_SPEED, HIGH_FREQUENCY_REQUEST_PACKET,
                                                HIGH_FREQUENCY_PIN)

# Initialize all messengers
client = mqtt.Client(MQTT_CLIENT_NAME)
mc_messenger = mc_messenger(client, HEARTBEAT_TIMEOUT_MC, SENDING_FREQUENCY_MC)
hercules_messenger = hercules_messenger([low_frequency_retriever, high_frequency_retriever], COMMAND_PIN)
spacex_messenger = udp_messenger(sending_frequency=SENDING_FREQUENCY_SPACEX)

# Initialize log
low_frequency_logger = mission_logger(LOW_FREQUENCY_LOG_FILE)
high_frequency_logger = mission_logger(HIGH_FREQUENCY_LOG_FILE)

run = True


def handle_received_commands():
    while mc_messenger.COMMAND_BUFFER.empty():
        hercules_messenger.send_command(mc_messenger.COMMAND_BUFFER.get())


try:
    while run:
        handle_received_commands()
        retrieved_data = hercules_messenger.retrieve_data()
        low_frequency_logger.log_data(low_frequency_logger)
        high_frequency_logger.log_data(high_frequency_logger)
        spacex_messenger.send_data(retrieved_data)
        if mc_messenger.is_mc_alive():
            mc_messenger.send_data(retrieved_data)
        else:
            mc_messenger.try_to_reconnect()
except KeyboardInterrupt:
    gpio.output(BRAKE_PIN, False)
    gpio.cleanup()
