import unittest
from messenger_ch import *
from mission_configs import *
import RPi.GPIO as gpio

messenger = mc_messenger(MQTT_BROKER_IP, MQTT_BROKER_PORT,
                         HEARTBEAT_TIMEOUT_MC, SENDING_FREQUENCY_MC,
                         data_handlers.HANDLE_MC_DATA)

dummy_data = list(range(125))


class TestStringMethods(unittest.TestCase):
    def test_emergency_brake(self):
        messenger.TRIGGER_EMERGENCY_BRAKE()
        gpio.setup(BRAKE_PIN, gpio.IN)
        self.assertFalse(gpio.input(BRAKE_PIN))
        gpio.setup(BRAKE_PIN, gpio.OUT)

    def test_emergency_brake_reset(self):
        messenger.TRIGGER_EMERGENCY_BRAKE()
        gpio.setup(BRAKE_PIN, gpio.IN)
        self.assertFalse(gpio.input(BRAKE_PIN))
        gpio.setup(BRAKE_PIN, gpio.OUT)
        time.sleep(2)
        gpio.setup(BRAKE_PIN, gpio.IN)
        self.assertTrue(gpio.input(BRAKE_PIN))
        gpio.setup(BRAKE_PIN, gpio.OUT)

    def test_mc_segmentor(self):
        segmented = data_handlers.HANDLE_MC_DATA(fullresponse=dummy_data)
        self.assertEqual(segmented, str(dummy_data))

    def test_spacex_segmentor(self):
        segmented = data_handlers.HANDLE_SPACEX_DATA(fullresponse=dummy_data)
        packer = struct.Struct('>BBlllllllL')
        data = packer.unpack(segmented)
        self.assertEqual(data, (1, 1, 124, 122, 123, 16, 100, 100, 100, 100))


initialize_Hub()
unittest.main()
gpio.output(BRAKE_PIN, gpio.LOW)
gpio.cleanup()
