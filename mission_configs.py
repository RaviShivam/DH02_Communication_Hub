import RPi.GPIO as gpio

"""
This file contains all the relevant constants that can be tweaked prior to the mission
"""

""" 
Constants that are defined for sending SpaceX UDP packages
"""
IP_ADRESS_SPACEX = "192.168.0.1"
PORT_SPACEX = 3000
SENDING_FREQUENCY_SPACEX = 8  # per seconds

"""
Logging constants
"""
HIGH_FREQUENCY_LOG_FILE = 'logs/highfreq.log'
LOW_FREQUENCY_LOG_FILE = 'logs/lowfreq.log'

""" 
Mission Control constants
"""
MILLIS = 1000.0
EMERGENCY_BRAKE_COMMAND = "EMERGENCY_BRAKE"
MQTT_BROKER_ADDRESS = 'localhost'
DATA_TOPIC = "data"
COMMAND_TOPIC = "mc/command"
HEARTBEAT_TOPIC = "mc/heartbeat"

MQTT_CLIENT_NAME = "COMMUNICATION HUB"
HEARTBEAT_TIMEOUT_MC = 1500  # milliseconds
# TODO: Make second timeout while accelerating.
SENDING_FREQUENCY_MC = 5  # p/second
PREFIX_MC = 0
POD_STATE_MC = 1
POD_SUBSTATE_MC = 2
ERROR_MC = 3
ERROR_ARGUMENT_MC = 4
TIMER_MC = 5
TARGETSPEED_MC = 6
BRAKEPOINT_MC = 7

"""
Constants for sending SPI packages to Hercules
"""
LOGGER_NAME_LOW_FREQUENCY = "logger-low-frequency"
LOGGER_NAME_HIGH_FREQUENCY = "logger-high-frequency"
LOW_DATA_RETRIEVAL_FREQUENCY = 4 #Hz
HIGH_DATA_RETRIEVAL_FREQUENCY = 25 #Hz
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

STATE_TRANSITION_COMMANDS = {
    "proceed_check_a": [0x01, 0x00],
    "proceed_check_b": [0x02, 0x00],
    "proceed_pump_idle": [0x03, 0x00],
    "proceed_check_c": [0x04, 0x00],
    "proceed_standstill": [0x05, 0x00],
    "launch": [0x06, 0x00],
    "service_propulsion": [0x07, 0x00],
    "abort": [0x08, 0x00],
    "proceed_shutdown": [0x09, 0x00],
    "get_status": [0x0A, 0xAA],
    "set_target_speed": [0x0B, 0xBB],
    "set_target_brakepoint": [0x0C, 0xCC]
}

HERCULES_STATES = {
    0x0000: "none",
    0x0100: "idle",
    0x0200: "check_a",
    0x0300: "check_b",
    0x0400: "pumpdown_idle",
    0x0500: "check_c",
    0x0600: "ready",
    0x0700: "acceleration",
    0x0800: "deceleration",
    0x0900: "standstill",
    0x0A00: "service_propulsion",
    0x0B00: "shutdown",
}

HERCULES_SUB_STATES = {
    0x0000: "none",
    0x0100: "busy",
    0x0200: "done",
    0x0300: "brake_brakepoint",
    0x0320: "brake_brakecommand",
    0x0350: "brake_communicationlost",
    0x03A0: "brake_timeexpired",
    0x03E0: "breake_sensorextreme"
}

HERCULES_ERROR_CODES = {
    0x0000: "error_none",
    0x0100: "error_system_check_failed",
    0x0200: "error_command_not_applicable",
    0x0300: "error_command_not_recognized",
    0x0400: "error_target_speed_not_set",
    0x0500: "error_brake_point_not_set"
}


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
