PREFIX = [0x0A, 0xAA]

nul = [0x00,0x00]
tail = [nul for _ in range(5)]

state_transition_commands = {
        "proceed_check_a": [0x01, 0x00],
        "proceed_check_b": [0x02, 0x00],
        "proceed_pump_idle": [0x03, 0x00],
        "proceed_check_c": [0x04, 0x00],
        "proceed_standstill": [0x05, 0x00],
        "launch": [0x06, 0x00],
        "service_propusion": [0x07, 0x00],
        "abort": [0x08, 0x00],
        "proceed_shutdown": [0x09, 0x00],
        "get_status": [0x0A, 0xAA],
        "set_target_speed": [0x0B, 0xBB],
        "set_target_brakepoint": [0x0C, 0xCC]
        }

hercules_states = {
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

hercules_sub_states = {
        0x000: "none",
        0x100: "busy",
        0x200: "done"
        }
