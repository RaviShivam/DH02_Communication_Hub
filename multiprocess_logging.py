import time
from mission_configs import *
from messenger_ch import spi16bit

spi = spi16bit()
initialize_Hub()
run = True
start = time.time()

c = 0
while run:
    c += 1
    spi.fast_xfer16(LOW_FREQUENCY_REQUEST_PACKET, CHIP_SELECT_CONFIG_LOW_FREQUENCY)
    if time.time() - start > 5:
        run = False

print("sampling frequency: {}".format(c/5))
