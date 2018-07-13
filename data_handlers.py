import struct
from mission_configs import *


def HANDLE_MC_DATA(fullresponse):
    return (str(fullresponse[0]), str(fullresponse[1]))

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
