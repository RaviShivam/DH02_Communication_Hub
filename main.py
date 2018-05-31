import RPi.GPIO as gpio
import os
import time
from messenger_ch import data_segmentor
from messenger_ch import hercules_comm_module
from messenger_ch import hercules_messenger
from messenger_ch import mc_messenger
from messenger_ch import mission_logger
from messenger_ch import udp_messenger
from mission_configs import *

# Create logs dir if it does not exist
if not os.path.exists("logs"):
    os.makedirs("logs")

# Set gpio pins used during the mission high.
initialize_GPIO()

# Initialize hercules communication module
low_frequency_data_retriever = hercules_comm_module(LOW_DATA_RETRIEVAL_FREQUENCY, LOW_FREQUENCY_REQUEST_PACKET,
                                                    CHIP_SELECT_CONFIG_LOW_FREQUENCY)

high_frequency_data_retriever = hercules_comm_module(HIGH_DATA_RETRIEVAL_FREQUENCY, HIGH_FREQUENCY_REQUEST_PACKET,
                                                     CHIP_SELECT_CONFIG_HIGH_FREQUENCY)

# Initialize hardware messenger
hercules_messenger = hercules_messenger([low_frequency_data_retriever, high_frequency_data_retriever],
                                        CHIP_SELECT_COMMAND)

# Initialize network messengers
mc_messenger = mc_messenger(MQTT_BROKER_IP, MQTT_BROKER_PORT,
                            HEARTBEAT_TIMEOUT_MC, SENDING_FREQUENCY_MC,
                            data_segmentor.SEGMENT_MC_DATA)

spacex_messenger = udp_messenger("10.42.0.1", 5005,
                                SENDING_FREQUENCY_SPACEX,
                                data_segmentor.SEGMENT_SPACEX_DATA)


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


def trigger_reconnecting_state():
    """
    This method is triggered when the Mission Control is disconnected.
    This handles the same procedure as the main loop, but waits to reconnect with the mission control.
    """
    gpio.output(BRAKE_PIN, False)
    while True:
        handle_received_commands()  # execute all commands in the command buffer
        hercules_messenger.poll_latest_data()  # retrieve data from hercules using data retrievers
        low_frequency_logger.log_data(low_frequency_data_retriever)  # Log the low frequency data
        high_frequency_logger.log_data(high_frequency_data_retriever)  # Log the high frequency data.

        spacex_messenger.send_data(hercules_messenger.latest_retrieved_data) # Send SpaceX data.

        if mc_messenger.is_mc_alive():  # Check if the mission control is alive
            break
    print("Reconnected. Entering normal state")
    gpio.output(BRAKE_PIN, True)

# boolean for running the main loop
run = True
try:
    while run:
        handle_received_commands()  # execute all commands in the command buffer
        hercules_messenger.poll_latest_data()  # retrieve data from hercules using data retrievers

        low_frequency_logger.log_data(low_frequency_data_retriever, console=False)  # Log the low frequency data
        high_frequency_logger.log_data(high_frequency_data_retriever, console=False)  # Log the high frequency data.

        spacex_messenger.send_data(hercules_messenger.latest_retrieved_data) # Send SpaceX data.

        if mc_messenger.is_mc_alive():  # Check if the mission control is alive
            mc_messenger.send_data(hercules_messenger.latest_retrieved_data)  # send data to mission control.
        # else:
            # print("Disconnected... Entering reconnection state.")
            # trigger_reconnecting_state()

except KeyboardInterrupt:
    gpio.output(BRAKE_PIN, gpio.LOW)
    gpio.cleanup()
