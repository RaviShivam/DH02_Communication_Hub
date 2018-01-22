import RPi.GPIO as gpio

"""
This file contains all the relevant constants that can be tweaked prior to the mission
"""

"""
Constants that are defined for sending SpaceX UDP packages
"""
IP_ADRESS_SPACEX = "192.168.0.1"
PORT_SPACEX = 3000
SENDING_FREQUENCY_SPACEX = 3 # per seconds

"""
Logging constants
"""
HIGH_FREQUENCY_LOG_FILE = 'logs/highfreq.log'
LOW_FREQUENCY_LOG_FILE = 'logs/lowfreq.log'

"""
Mission Control constants
"""
MILLIS = 1000.0
EMERGENCY_BRAKE_COMMAND = 0x0dec
MQTT_BROKER_ADDRESS = 'localhost'
DATA_TOPIC = "data"
COMMAND_TOPIC = "mc/command"
HEARTBEAT_TOPIC = "mc/heartbeat"

MQTT_CLIENT_NAME = "COMMUNICATION HUB"
HEARTBEAT_TIMEOUT_MC = 1500  # milliseconds
# TODO: Make second timeout while accelerating.
SENDING_FREQUENCY_MC = 5  # p/second

"""
Constants for sending SPI packages to Hercules
"""
LOGGER_NAME_LOW_FREQUENCY = "logger-low-frequency"
LOGGER_NAME_HIGH_FREQUENCY = "logger-high-frequency"
LOW_DATA_RETRIEVAL_FREQUENCY = 1 #Hz
HIGH_DATA_RETRIEVAL_FREQUENCY = 1 #Hz
SPI_FREQUENCY_HERCULES = 2000000 #Hz

BRAKE_PIN = 21
CS0 = 13
CS1 = 19
CS2 = 26

ALL_CS = [CS0, CS1, CS2]

CHIP_SELECT_COMMAND = [(CS0, True), (CS1, False), (CS2, False)]
CHIP_SELECT_CONFIG_HIGH_FREQUENCY = [(CS0, False), (CS1, True), (CS2, False)]
CHIP_SELECT_CONFIG_LOW_FREQUENCY = [(CS0, True), (CS1, True), (CS2, False)]

ZPACKET = [0x00, 0x00]
MASTER_PREFIX = [0x0A, 0xAA]
HIGH_FREQUENCY_PACKET_LENGTH = 4 #times 16 bits
LOW_FREQUENCY_PACKET_LENGTH = 119 #times 119 bits

# COMMAND_REQUEST_PACKET = [MASTER_PREFIX] + [ZPACKET for _ in range(2)] #DEBUGGGGG
HIGH_FREQUENCY_REQUEST_PACKET = [MASTER_PREFIX] + [ZPACKET for _ in range(HIGH_FREQUENCY_PACKET_LENGTH)]
LOW_FREQUENCY_REQUEST_PACKET = [MASTER_PREFIX] + [ZPACKET for _ in range(LOW_FREQUENCY_PACKET_LENGTH)]

POD_ACCELERATION_STATE = 0x0600

def initialize_GPIO():
    gpio.setwarnings(False)
    gpio.setmode(gpio.BCM)
    gpio.setup(BRAKE_PIN, gpio.OUT)
    gpio.setup(CS0, gpio.OUT)
    gpio.setup(CS2, gpio.OUT)
    gpio.setup(CS1, gpio.OUT)
    gpio.output(BRAKE_PIN, True)
    gpio.output(CS0, True)
    gpio.output(CS1, True)
    gpio.output(CS2, True)
