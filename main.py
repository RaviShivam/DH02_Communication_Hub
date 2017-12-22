import RPi.GPIO as gpio
import paho.mqtt.client as mqtt

from messenger_ch import data_segmentor
from messenger_ch import hercules_comm_module
from messenger_ch import hercules_messenger
from messenger_ch import mc_messenger
from messenger_ch import mission_logger
from messenger_ch import udp_messenger
from mission_configs import *

# Set gpio pins used during the mission high.
initialize_GPIO()

# Initialize hercules communication module
low_frequency_data_retriever = hercules_comm_module(LOW_DATA_RETRIEVAL_FREQUENCY, LOW_FREQUENCY_REQUEST_PACKET,
                                                    CHIP_SELECT_CONFIG_LOW_FREQUENCY)
high_frequency_data_retriever = hercules_comm_module(HIGH_DATA_RETRIEVAL_FREQUENCY, HIGH_FREQUENCY_REQUEST_PACKET,
                                                     CHIP_SELECT_CONFIG_HIGH_FREQUENCY)

# Initialize all messengers
client = mqtt.Client(MQTT_CLIENT_NAME)
mc_messenger = mc_messenger(client, HEARTBEAT_TIMEOUT_MC, SENDING_FREQUENCY_MC)
hercules_messenger = hercules_messenger([low_frequency_data_retriever, high_frequency_data_retriever],
                                        CHIP_SELECT_COMMAND)
spacex_messenger = udp_messenger(sending_frequency=SENDING_FREQUENCY_SPACEX)

# Initialize loggers
low_frequency_logger = mission_logger(LOGGER_NAME_LOW_FREQUENCY, LOW_FREQUENCY_LOG_FILE)
high_frequency_logger = mission_logger(LOGGER_NAME_HIGH_FREQUENCY, HIGH_FREQUENCY_LOG_FILE)


# Initialize segmentors
data_segmentor = data_segmentor()

def handle_received_commands():
    """
    Loops through the entire command buffer and executes all command enqueued in it.
    The buffer is emptied iteratively after each command execution
    :return: None
    """
    while not mc_messenger.COMMAND_BUFFER.empty():
        command = mc_messenger.COMMAND_BUFFER.get()
        hercules_messenger.send_command(command)


# boolean for running the main loop
run = True
try:
    while run:
        handle_received_commands()  # execute all commands in the command buffer
        retrieved_data = hercules_messenger.retrieve_data()  # retrieve data from hercules using data retrievers
        low_frequency_logger.log_data(low_frequency_data_retriever)  # Log the low frequency data
        high_frequency_logger.log_data(high_frequency_data_retriever)  # Log the high frequency data.
        # spacex_messenger.send_data(retrieved_data) # Send SpaceX data.
        if mc_messenger.is_mc_alive():  # Check if the mission control is alive
            mc_messenger.send_data(data_segmentor.segment_mc_data(retrieved_data))  # send data to mission control.
        else:
            mc_messenger.try_to_reconnect()  # debug reconnecting.
except KeyboardInterrupt:
    gpio.output(BRAKE_PIN, False)
    gpio.cleanup()
