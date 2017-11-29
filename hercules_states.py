state_commands = {
        "check_a": [0x01, 0x00],
        "check_b": [0x02, 0x00],
        "check_c": [0x03, 0x00],
        "check_d": [0x04, 0x00],
        "pump_idle": [0x05, 0x00],
        "standstil": [0x06, 0x00],
        "launch": [0x07, 0x00],
        "service": [0x08, 0x00],
        "abort": [0x0A, 0x00],
        "heartbeat": [0x0D, 0xDD]
        }

hercules_states = {
        '0x100': "idle",
        '0x200': "check_a",
        '0x300': "check_b",
        '0x400': "pump_idle",
        '0x500': "check_c",
        '0x600': "Ready",
        '0x700': "Accelaration",
        '0x800': "Deceleration",
        '0x900': "Standstil",
        '0xA00': "Service propulsion",
        '0xB00': "System check D",
        '0xC00': "No communication",
        '0xD00': "Watchdog expired",
        '0xE00': "Error"
        }

hercules_sub_states = {
        '0x000': "None",
        '0x100': "Busy",
        '0x200': "Done"
        }
