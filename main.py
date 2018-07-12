import RPi.GPIO as gpio
import os
import time
from data_handlers import *
from messenger_ch import hercules_comm_module
from messenger_ch import hercules_messenger
from messenger_ch import mc_messenger
from messenger_ch import mission_logger
from messenger_ch import mission_logger
from messenger_ch import udp_messenger
from mission_configs import *

# Create logs dir if it does not exist
if not os.path.exists("/home/pi/DH02_Communication_Hub/logs"):
    os.makedirs("/home/pi/DH02_Communication_Hub/logs")

# Set gpio pins used during the mission high.
initialize_Hub()

# initialize loggers
low_frequency_logger = mission_logger(logger_name=LOGGER_NAME_LOW_FREQUENCY,
                                      file=LOW_FREQUENCY_LOG_FILE,
                                      handle_data=HANDLE_LOG)

high_frequency_logger = mission_logger(logger_name=LOGGER_NAME_HIGH_FREQUENCY,
                                       file=HIGH_FREQUENCY_LOG_FILE,
                                       handle_data=HANDLE_LOG)

# Initialize hercules communication module
low_frequency_data_retriever = hercules_comm_module(retrieving_frequency=LOW_DATA_RETRIEVAL_FREQUENCY,
                                                    request_packet=LOW_FREQUENCY_REQUEST_PACKET,
                                                    comm_config=CHIP_SELECT_CONFIG_LOW_FREQUENCY,
                                                    handle_data=HANDLE_LOW_F_DATA,
                                                    logger=low_frequency_logger)

high_frequency_data_retriever = hercules_comm_module(retrieving_frequency=HIGH_DATA_RETRIEVAL_FREQUENCY,
                                                     request_packet=HIGH_FREQUENCY_REQUEST_PACKET,
                                                     comm_config=CHIP_SELECT_CONFIG_HIGH_FREQUENCY,
                                                     handle_data=HANDLE_HIGH_F_DATA,
                                                     logger=high_frequency_logger)

# Initialize Hercules messenger
hercules_messenger = hercules_messenger(data_modules=[low_frequency_data_retriever, high_frequency_data_retriever],
                                        command_config=CHIP_SELECT_COMMAND)

# Initialize mission control messenger
mc_messenger = mc_messenger(broker_ip=MQTT_BROKER_IP,
                            broker_port=MQTT_BROKER_PORT,
                            mc_heartbeat_timeout=HEARTBEAT_TIMEOUT_MC,
                            low_frequency=SENDING_FREQUENCY_MC_LOW,
                            high_frequency=SENDING_FREQUENCY_MC_HIGH,
                            handle_data=HANDLE_MC_DATA)

# Initialize SpaceX messenger
spacex_messenger = udp_messenger(ip_adress=IP_ADRESS_SPACEX,
                                 port=PORT_SPACEX,
                                 sending_frequency=SENDING_FREQUENCY_SPACEX,
                                 handle_data=HANDLE_SPACEX_DATA)


def handle_received_commands():
    """
    Loops through the entire command buffer and executes all command enqueued in it.
    The buffer is emptied iteratively after each command execution
    :return: None
    """
    while not mc_messenger.COMMAND_BUFFER.empty():
        command = mc_messenger.COMMAND_BUFFER.get()
        if command[0] == RESET_COMMAND:
            hercules_messenger.INITIALIZE_HERCULES()
        else:
            hercules_messenger.send_command(command)


def trigger_reconnecting_state():
    """
    This method is triggered when the Mission Control is disconnected.
    This handles the same procedure as the main loop, but waits to reconnect with the mission control.
    """
    gpio.output(BRAKE_PIN, False)
    while True:
        # Execute all commands in the command buffer
        handle_received_commands()

        # Retrieve data from hercules using data retrievers
        hercules_messenger.poll_latest_data()

        # Send SpaceX data.
        spacex_messenger.send_data(hercules_messenger.latest_retrieved_data)

        # Check if the mission control is alive
        if mc_messenger.is_mc_alive():
            break
    print("Reconnected. Entering normal state")
    gpio.output(BRAKE_PIN, True)


# Sync message alignment with hercules at startup.
time.sleep(1)
#hercules_messenger.INITIALIZE_HERCULES()

# Boolean for running the main loop
run = True

try:
    while run:
        # Send all commands in the command buffer
        handle_received_commands()

        # Retrieve and log data from hercules
        hercules_messenger.poll_latest_data()

        # Send SpaceX data.
        spacex_messenger.send_data(hercules_messenger.latest_retrieved_data)

        mc_messenger.send_data(hercules_messenger.latest_retrieved_data)

        # # Check if the mission control is alive
        # if mc_messenger.is_mc_alive():
        #     # Send data to Mission Control.
        #     mc_messenger.send_data(hercules_messenger.latest_retrieved_data)
        # else:
        #     print("Disconnected... Entering reconnection state.")
        #     trigger_reconnecting_state()

except KeyboardInterrupt:
    cleanup_Hub()

cleanup_Hub()
