import os
import time
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.FileHandler('/home/pi/temperature.log')
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s, %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Return CPU temperature as a character string
def getCPUtemperature():
    res = os.popen('vcgencmd measure_temp').readline()
    return(res.replace("temp=","").replace("'C\n",""))

while True:
    logger.info(getCPUtemperature())
    time.sleep(10)
