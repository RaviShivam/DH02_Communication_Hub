import time
from messenger_ch import hercules_comm_module
from messenger_ch import hercules_messenger
from mission_configs import *

# Initialize hercules communication module
low_frequency_retriever = hercules_comm_module(LOW_DATA_RETRIEVAL_FREQUENCY, LOW_FREQUENCY_REQUEST_PACKET,
                                               CHIP_SELECT_CONFIG_LOW_FREQUENCY)
# Initialize all messengers
hercules_messenger = hercules_messenger([low_frequency_retriever], CHIP_SELECT_COMMAND)

initialize_GPIO()

run = True

counter = 0
try:
    while run:
        retrieved_data = hercules_messenger.retrieve_data()
        print(retrieved_data)
        time.sleep(0.2)
except KeyboardInterrupt:
    gpio.output(BRAKE_PIN, False)
    gpio.cleanup()
