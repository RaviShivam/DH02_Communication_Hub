import struct

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
