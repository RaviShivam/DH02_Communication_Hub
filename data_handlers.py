import struct
from mission_configs import *


def HANDLE_MC_DATA(fullresponse):
    return (str(fullresponse[0]), str(fullresponse[1]))


def HANDLE_SPACEX_DATA(fullresponse):
    parse_16s_to_float = lambda x1, x2: struct.unpack('>f', bytes.fromhex(
        format((x1 << 16 | x2), 'x').zfill(8)))[0] if x1 is not 0 or x2 is not 0 else 0

    complete = fullresponse[0] + fullresponse[1]
    team_id = TEAM_ID
    accelaration = int(parse_16s_to_float(complete[INDEX_ACCELARATION], complete[INDEX_ACCELARATION + 1]) * 100)
    position = int(parse_16s_to_float(complete[INDEX_POSITION], complete[INDEX_POSITION + 1]) * 100)
    velocity = int(parse_16s_to_float(complete[INDEX_VELOCITY], complete[INDEX_VELOCITY + 1]) * 100)

    battery_voltage = complete[INDEX_BATTERY_VOLTAGE]
    battery_current = complete[INDEX_BATTERY_CURRENT]
    battery_temp = complete[INDEX_BATTERY_TEMPERATURE]

    pod_temperature = complete[INDEX_STRIPE_COUNT]
    stripe_count = max(complete[INDEX_STRIPE_COUNT], complete[INDEX_STRIPE_COUNT + 1])

    packer = struct.Struct('>BBlllllllL')
    return packer.pack(team_id, accelaration, position, velocity, battery_voltage, battery_current, battery_temp,
                       pod_temperature, stripe_count)


def HANDLE_LOG(data):
    return ", ".join(str(x) for x in data)
