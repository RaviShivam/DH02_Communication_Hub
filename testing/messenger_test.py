import unittest
import time
import RPi.GPIO as gpio
from ...messenger_ch import *
from ...mission_configs import *

class TestStringMethods(unittest.TestCase):
    def test_split(self):
        mc_messenger = mc_messenger(MQTT_BROKER_IP, MQTT_BROKER_PORT,
                                    HEARTBEAT_TIMEOUT_MC, SENDING_FREQUENCY_MC,
                                    data_segmentor.HANDLE_MC_DATA)
        mc_messenger.TRIGGER_EMERGENCY_BRAKE
        self.assertEqual(gpio.output(BRAKE_PIN), False)
        time.sleep(1)
        self.assertEqual(gpio.output(BRAKE_PIN), True)

if __name__ == '__main__':
    unittest.main()
