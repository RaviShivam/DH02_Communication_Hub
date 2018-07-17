import struct
from mission_configs import *


def HANDLE_MC_DATA(fullresponse):
    return (str(fullresponse[0]), str(fullresponse[1]))


def HANDLE_SPACEX_DATA(fullresponse):
    parse_16s_to_float = lambda x1, x2: struct.unpack('>f', bytes.fromhex(
        format((x1 << 16 | x2), 'x').zfill(8)))[0] if x1 is not 0 or x2 is not 0 else 0

    complete = fullresponse[0] + fullresponse[1]
    team_id = TEAM_ID
    status = SPACEX_POD_STATE[complete[INDEX_POD_STATE]] if complete[INDEX_POD_STATE] in SPACEX_POD_STATE else 1

    accelaration = int(parse_16s_to_float(complete[INDEX_ACCELARATION], complete[INDEX_ACCELARATION + 1]) * 100)
    position = int(parse_16s_to_float(complete[INDEX_POSITION], complete[INDEX_POSITION + 1]) * 100)
    velocity = int(parse_16s_to_float(complete[INDEX_VELOCITY], complete[INDEX_VELOCITY + 1]) * 100)

    battery_voltage = (complete[INDEX_BATTERY_VOLTAGE] + 30000) * 10

    battery_current = (complete[INDEX_BATTERY_CURRENT] - 65536 if complete[INDEX_BATTERY_CURRENT] > 32767 else complete[INDEX_BATTERY_CURRENT]) * 100
    print(complete[INDEX_BATTERY_CURRENT])
    battery_temp = (complete[INDEX_BATTERY_TEMPERATURE] - 100) * 10
    pod_temperature = 0
    stripe_count = max(complete[INDEX_STRIPE_COUNT], complete[INDEX_STRIPE_COUNT + 1])

    packer = struct.Struct('>BBiiiiiiiI')
    try:
        packed_data = packer.pack(team_id, status, accelaration, position, velocity, battery_voltage, battery_current, battery_temp, pod_temperature, stripe_count)
    except struct.error:
        print("Unable to pack data in SpaceX format")
        packed_data = packer.pack(team_id, status, 0, 0, 0, 0, 0, 0, 0, 0)
    return packed_data

def HANDLE_HIGH_F_PROCESSED(data):
    parse_16s_to_float = lambda x1, x2: struct.unpack('>f', bytes.fromhex(
        format((x1 << 16 | x2), 'x').zfill(8)))[0] if x1 is not 0 or x2 is not 0 else 0
    process_data = [data[0],                                # prefix             (100)
                    parse_16s_to_float(data[1], data[2]),   # projected position (101)
                    parse_16s_to_float(data[3], data[4]),   # projected velocity (102)
                    data[5],                                # motor rpm      (103)
                    parse_16s_to_float(data[6], data[7]),   # acceleration X (104)
                    parse_16s_to_float(data[8], data[9]),   # acceleration Y (105)
                    parse_16s_to_float(data[10], data[11]), # acceleration Z (106)
                    data[12],                               # Diffuse left   (107)
                    data[13],                               # Diffuse right  (108)
                    parse_16s_to_float(data[14], data[15]), # Gyr x          (109)
                    parse_16s_to_float(data[16], data[17]), # Gyr y          (110)
                    parse_16s_to_float(data[18], data[19])  # Gyr z          (111)
                    ]
    return process_data

def HANDLE_LOG(data):
    return ", ".join(str(x) for x in data)
