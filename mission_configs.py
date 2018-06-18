import RPi.GPIO as gpio

"""
This file contains all the relevant constants that can be adjusted prior to the mission
"""

#######################################################################################################################
######################################### SPACEX MESSENGERS CONSTANTS #################################################
#######################################################################################################################
POD_ACCELERATION_STATE = 0x0600

# Constants that are defined for sending SpaceX UDP packages
IP_ADRESS_SPACEX = "192.168.0.1"
PORT_SPACEX = 3000
SENDING_FREQUENCY_SPACEX = 10  # per seconds

# Creation of the UDP package.
TEAM_ID = 1  # TODO: Should be changed during competition
INDEX_POD_STATE = 2
INDEX_ACCELARATION = 105
INDEX_POSITION = 101
INDEX_VELOCITY = 103
INDEX_BATTERY_VOLTAGE = 32
INDEX_BATTERY_CURRENT = 33
INDEX_BATTERY_TEMPERATURE = 28
INDEX_POD_TEMPERATURE = 28
INDEX_STRIPE_COUNT = 112

SPACEX_POD_STATE = {
    0: 1,  # 0x0000  (NONE)
    256: 1,  # 0x0100 (IDLE)
    512: 1,  # 0x0200 (TEST_A)
    768: 1,  # 0x0300 (TEST_B)
    1024: 1,  # 0x0400 (PUMPDOWN)
    1280: 1,  # 0x0500 (TEST_C)
    1536: 2,  # 0x0600 (READY)
    1792: 3,  # 0x0700 (ACCELERATION)
    2048: 5,  # 0x0800 (DECELERATION)
    2204: 1,  # 0x0900 (STANDSTILL)
    2560: 1,  # 0x0A00 (TEST_D)
    2816: 1,  # 0x0B00 (TEST_E)
    3072: 1  # 0x0C00 (CHARGING)
}

#######################################################################################################################
########################################### DATA LOGGER CONSTANTS #####################################################
#######################################################################################################################
# TODO: Give file names better name.
HIGH_FREQUENCY_LOG_FILE = '/home/pi/DH02_Communication_Hub/logs/highfreq.log'
LOW_FREQUENCY_LOG_FILE = '/home/pi/DH02_Communication_Hub/logs/lowfreq.log'

#######################################################################################################################
##################################### MISSION CONTROL MESSENGER CONSTANTS #############################################
#######################################################################################################################
MILLIS = 1000.0
MQTT_BROKER_IP = 'localhost'
MQTT_BROKER_PORT = 1883
LOW_DATA_TOPIC = "data/low"
HIGH_DATA_TOPIC = "data/high"
COMMAND_TOPIC = "mc/command"
HEARTBEAT_TOPIC = "mc/heartbeat"
EMERGENCY_BRAKE_COMMAND = 0x0dec  # 3564
RESET_COMMAND = 0x0ffff  # 65535

MQTT_CLIENT_NAME = "COMMUNICATION HUB"
HEARTBEAT_TIMEOUT_MC = 5000  # milliseconds
# TODO: Make second timeout while accelerating.
SENDING_FREQUENCY_MC_LOW = 10  # p/second
SENDING_FREQUENCY_MC_HIGH = 30  # p/second

LOGGER_NAME_LOW_FREQUENCY = "logger-low-frequency"
LOGGER_NAME_HIGH_FREQUENCY = "logger-high-frequency"

# Define functional pins on the Communication Hub
BRAKE_PIN = 19
RESET_PIN = 27

#######################################################################################################################
####################################### HERCULES MESSENGER SPI CONSTANTS ##############################################
#######################################################################################################################
# Constants for sending SPI packages to Hercules
LOW_DATA_RETRIEVAL_FREQUENCY = 20  # Hz
HIGH_DATA_RETRIEVAL_FREQUENCY = 1500  # Hz
SPI_FREQUENCY_HERCULES = 1000000  # Hz

# Chip selects for the SPI link
CS0 = 5
CS1 = 6
CS2 = 13
ALL_CS = [CS0, CS1, CS2]

# Communication chip selects
CHIP_SELECT_COMMAND = [(CS0, True), (CS1, False), (CS2, False)]
CHIP_SELECT_CONFIG_HIGH_FREQUENCY = [(CS0, False), (CS1, True), (CS2, False)]
CHIP_SELECT_CONFIG_LOW_FREQUENCY = [(CS0, True), (CS1, True), (CS2, False)]

# Length of packets expected from the Hercules SPI link
HIGH_FREQUENCY_PACKET_LENGTH = 28  # times 16 bits
LOW_FREQUENCY_PACKET_LENGTH = 99  # times 16 bits

# Define standard packet protocols for the SPI
MASTER_PREFIX = [0x0A, 0xAA]
SLAVE_PREFIX = [0x02, 0x00]

# Generate request packets for the SPI
HIGH_FREQUENCY_REQUEST_PACKET = MASTER_PREFIX + [0 for _ in range(HIGH_FREQUENCY_PACKET_LENGTH * 2)]
LOW_FREQUENCY_REQUEST_PACKET = MASTER_PREFIX + [0 for _ in range(LOW_FREQUENCY_PACKET_LENGTH * 2)]


#######################################################################################################################
########################################### CONFIGURATION SCRIPTS #####################################################
#######################################################################################################################
def initialize_Hub():
    gpio.setwarnings(False)
    gpio.setmode(gpio.BCM)
    gpio.setup(BRAKE_PIN, gpio.OUT)
    gpio.setup(CS0, gpio.OUT)
    gpio.setup(CS2, gpio.OUT)
    gpio.setup(CS1, gpio.OUT)
    gpio.setup(RESET_PIN, gpio.OUT)
    gpio.output(BRAKE_PIN, True)
    gpio.output(CS0, True)
    gpio.output(CS1, True)
    gpio.output(CS2, True)
    gpio.output(RESET_PIN, True)


def cleanup_Hub():
    gpio.output(BRAKE_PIN, gpio.LOW)
    gpio.cleanup()
