import struct
from mission_configs import *


def HANDLE_MC_DATA(fullresponse):
    return (str(fullresponse[0]), str(fullresponse[1]))


def HANDLE_LOW_F_DATA(data):
    # Keep option open for processing low frequency data.
    return data


def HANDLE_HIGH_F_DATA(data):
    parse_16s_to_float = lambda x1, x2: struct.unpack('>f', bytes.fromhex(
        format((x1 << 16 | x2), 'x').zfill(8)))[0] if x1 is not 0 or x2 is not 0 else 0

    # process_data = [data[0],                                # prefix             (100)
    #                 parse_16s_to_float(data[1], data[2]),   # projected position (101)
    #                 parse_16s_to_float(data[3], data[4]),   # projected velocity (102)
    #                 data[5],                                # motor rpm      (103)
    #                 parse_16s_to_float(data[6], data[7]),   # acceleration X (104)
    #                 parse_16s_to_float(data[8], data[9]),   # acceleration Y (105)
    #                 parse_16s_to_float(data[10], data[11]), # acceleration Z (106)
    #                 data[12],                               # Diffuse left   (107)
    #                 data[13],                               # Diffuse right  (108)
    #                 parse_16s_to_float(data[14], data[15]), # Gyr x          (109)
    #                 parse_16s_to_float(data[16], data[17]), # Gyr y          (110)
    #                 parse_16s_to_float(data[18], data[19])  # Gyr z          (111)
    #                 ]
    process_data = [data[0],                                    # prefix
                   parse_16s_to_float(0x411c, 0xfe72),       # projected position
                   parse_16s_to_float(0x41a0, 0xfc56),       # projected velocity
                   data[5],                                    # motor rpm
                   parse_16s_to_float(0x411c, 0xfe72),       # projected position
                   parse_16s_to_float(0x41a0, 0xfc56),       # projected velocity
                   parse_16s_to_float(0x41a0, 0xfc50),       # projected velocity
                   data[12],                                   # Diffuse left
                   data[13],                                   # Diffuse right
                   parse_16s_to_float(0x411c, 0xfe72),       # projected position
                   parse_16s_to_float(0x41a0, 0xfc56),       # projected velocity
                   parse_16s_to_float(0x41a0, 0xfc50),       # projected velocity
                   ]
    return process_data


def HANDLE_SPACEX_DATA(fullresponse):
    fullresponse = fullresponse[0] + fullresponse[1]
    data = []
    data.append(TEAM_ID)
    if fullresponse[INDEX_POD_STATE] in SPACEX_POD_STATE:
        data.append(SPACEX_POD_STATE[fullresponse[INDEX_POD_STATE]])
    else:
        data.append(1)
    data.append(int(fullresponse[INDEX_ACCELARATION] * 100)) # (104) accelaration in cm/s^2
    data.append(int(fullresponse[INDEX_POSITION] * 100))     # (101) position in cm
    data.append(int(fullresponse[INDEX_VELOCITY] * 100))          # (102) velocity in cm/s
    data.append(fullresponse[INDEX_BATTERY_VOLTAGE])
    data.append(fullresponse[INDEX_BATTERY_CURRENT])
    data.append(fullresponse[INDEX_BATTERY_TEMPERATURE])
    data.append(fullresponse[INDEX_POD_TEMPERATURE])
    data.append(max(fullresponse[INDEX_STRIPE_COUNT_LEFT], fullresponse[INDEX_STRIPE_COUNT_RIGHT])) # Highest of 107 and 108
    packer = struct.Struct('>BBlllllllL')
    return packer.pack(*data)


def HANDLE_LOG(data):
    return ", ".join(str(x) for x in data)
