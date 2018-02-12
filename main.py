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
# spacex_messenger = udp_messenger(sending_frequency=SENDING_FREQUENCY_SPACEX)
spacex_messenger = udp_messenger(ip_adress="10.42.0.1", port=5005, sending_frequency=SENDING_FREQUENCY_SPACEX)

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
    GPIO.output(BRAKE_PIN, False)
    while True:
        handle_received_commands()  # execute all commands in the command buffer
        hercules_messenger.poll_latest_data()  # retrieve data from hercules using data retrievers
        low_frequency_logger.log_data(low_frequency_data_retriever)  # Log the low frequency data
        high_frequency_logger.log_data(high_frequency_data_retriever)  # Log the high frequency data.

        spacex_messenger.send_data(hercules_messenger.latest_retrieved_data) # Send SpaceX data.

        if mc_messenger.is_mc_alive():  # Check if the mission control is alive
            break
    print("Reconnected...")
    GPIO.output(BRAKE_PIN, True)


# boolean for running the main loop
run = True
try:
    while run:
        handle_received_commands()  # execute all commands in the command buffer
        hercules_messenger.poll_latest_data()  # retrieve data from hercules using data retrievers
        low_frequency_logger.log_data(low_frequency_data_retriever)  # Log the low frequency data
        high_frequency_logger.log_data(high_frequency_data_retriever)  # Log the high frequency data.

        spacex_messenger.send_data(hercules_messenger.latest_retrieved_data) # Send SpaceX data.

        if mc_messenger.is_mc_alive():  # Check if the mission control is alive
            mc_messenger.send_data(hercules_messenger.latest_retrieved_data)  # send data to mission control.
        else:
            print("Disconnected... Entering reconnection state.")
            trigger_reconnecting_state()

except KeyboardInterrupt:
    gpio.output(BRAKE_PIN, gpio.LOW)
    gpio.cleanup()
