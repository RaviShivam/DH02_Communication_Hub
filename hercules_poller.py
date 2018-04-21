import RPi.GPIO as gpio

import time
from messenger_ch import hercules_comm_module
from messenger_ch import hercules_messenger
from mission_configs import *

# Set gpio pins used during the mission high.
initialize_GPIO()

# Initialize hercules communication module
low_frequency_data_retriever = hercules_comm_module(LOW_DATA_RETRIEVAL_FREQUENCY, LOW_FREQUENCY_REQUEST_PACKET, CHIP_SELECT_CONFIG_LOW_FREQUENCY)

high_frequency_data_retriever = hercules_comm_module(HIGH_DATA_RETRIEVAL_FREQUENCY, HIGH_FREQUENCY_REQUEST_PACKET, CHIP_SELECT_CONFIG_HIGH_FREQUENCY)

# Initialize hardware messenger
hercules_messenger = hercules_messenger([low_frequency_data_retriever, high_frequency_data_retriever],
                                        CHIP_SELECT_COMMAND)

# boolean for running the main loop
run = True
try:
    while run:
        hercules_messenger.poll_latest_data()  # retrieve data from hercules using data retrievers
        if (hercules_messenger.latest_retrieved_data[0] is not None):
            print([hex(x) for x in hercules_messenger.latest_retrieved_data[0]])
            print([hex(x) for x in hercules_messenger.latest_retrieved_data[1]])
        time.sleep(1)
        
except KeyboardInterrupt:
    gpio.output(BRAKE_PIN, gpio.LOW)
    gpio.cleanup()
