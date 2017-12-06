"""
This file contains all the relevant constants that can be tweaked prior to the mission
"""

""" 
Constants that are defined for sending SpaceX UDP packages
"""
IP_ADRESS_SPACEX = "192.168.0.1"
PORT_SPACEX = 3000
SENDING_FREQUENCY_SPACEX = 8 #per seconds


""" 
Mission Control constants
"""
MQTT_CLIENT_NAME = "COMMUNICATION HUB"
HEARTBEAT_TIMEOUT_MC = 1500 #milliseconds
SENDING_FREQUENCY_MC = 5 #p/second
LOGGING_FREQUENCY = 5 #p/second
PREFIX_MC = "prefix"
POD_STATE_MC =  "podState"
POD_SUBSTATE_MC = "podSubstate"
ERROR_MC = "error"
ERROR_ARGUMENT_MC = "errorArgument"
TIMER_MC = "timer"
TARGETSPEED_MC = "targetSpeed"
BRAKEPOINT_MC = "brakePoint"


"""
Constants for sending SPI packages to Hercules
"""
SENDING_FREQUENCY_HERCULES = 1 #per seconds
BRAKE_PIN = 21

MASTER_PREFIX = [0x0A, 0xAA]
SPI_DATA_TAIL = [[0x00, 0x00] for _ in range(5)]
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
