import logging
import socket
import threading
import time

import RPi.GPIO as gpio
import spidev

from mission_configs import *

MILLIS = 1000.0

pod_status = {PREFIX_MC: "undefined",
              POD_STATE_MC: "undefined",
              POD_SUBSTATE_MC: "undefined",
              ERROR_MC: "undefined",
              ERROR_ARGUMENT_MC: "undefined",
              TIMER_MC: "undefined",
              TARGETSPEED_MC: "undefined",
              BRAKEPOINT_MC: "undefined"}


class abstract_messenger:
    def __init__(self, sending_frequency):
        self.current_time_millis = lambda: time.time() * MILLIS
        self.last_sent_timeout = MILLIS / float(sending_frequency)
        self.last_sent = self.current_time_millis()

    def time_for_sending_data(self):
        last_sent_exceeded = (self.current_time_millis() - self.last_sent) > self.last_sent_timeout
        return last_sent_exceeded

    def reset_last_sent_timer(self):
        self.last_sent = self.current_time_millis()


class mc_messenger(abstract_messenger):
    def __init__(self, client, hercules_messenger, mc_heartbeat_timeout, sending_frequency=8):
        super(mc_messenger, self).__init__(sending_frequency)
        self.data_topic = "data"
        self.command_topic = "mc/command"
        self.heartbeat_topic = "mc/heartbeat"

        # Heartbeat configurations
        self.heartbeat_timeout = mc_heartbeat_timeout
        self.last_heartbeat = self.current_time_millis()
        self.is_mc_alive = lambda: (self.current_time_millis() - self.last_heartbeat) < self.heartbeat_timeout

        # Initialize client and start separate thread for receiving commands
        self.client = client
        self.hercules_messenger = hercules_messenger
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect("localhost", 1883, 60)
        threading.Thread(target=self.client.loop_forever).start()

    def on_connect(self, client, userdata, flags, rc):
        client.subscribe(self.command_topic)
        client.subscribe(self.heartbeat_topic)
        print("Connected to all topics")

    def on_message(self, client, userdata, msg):
        self.last_heartbeat = self.current_time_millis()
        topic, command = msg.topic, msg.payload.decode()
        if topic == self.command_topic:
            if command == "ebrake":
                self.hercules_messenger.BRAKE()
            else:
                message = msg.payload.decode().split(":")
                command = message[0]
                argument = int(message[1])
                self.hercules_messenger.send_command(command, argument)

    def send_data(self, data):
        if self.time_for_sending_data():
            self.client.publish(self.data_topic, payload=data, qos=0)
            self.reset_last_sent_timer()


class udp_messenger(abstract_messenger):
    def __init__(self, ip_adress="192.168.0.1", port=3000, sending_frequency=10):
        super(udp_messenger, self).__init__(sending_frequency)
        self.TARGET_IP = ip_adress
        self.TARGET_PORT = port
        self.sock = socket.socket(socket.AF_INET,
                                  socket.SOCK_DGRAM)

    def send_data(self, data):
        if self.time_for_sending_data():
            self.sock.sendto(data, (self.TARGET_IP, self.TARGET_PORT))
            self.reset_last_sent_timer()


class hercules_messenger(abstract_messenger):
    def __init__(self, sending_frequency=4):
        super(hercules_messenger, self).__init__(sending_frequency)
        self.brake_pin = 21
        gpio.setmode(gpio.BCM)
        gpio.setup(self.brake_pin, gpio.OUT)
        gpio.output(self.brake_pin, True)

        self.spi = spidev.SpiDev()
        self.spi.open(0, 0)
        self.spi.max_speed_hz = 500000

        self.hercules_translator = hercules_decoder()

    def xfer16(self, data):
        response = [self.spi.xfer(packet) for packet in data]
        processed = list()
        for i in response:
            processed.append((i[0] << 8) + i[1])
        return processed


    def get_pod_status(self):
        if self.time_for_sending_data():
            self.send_command("get_status", 0)
            self.reset_last_sent_timer()
        return pod_status

    def send_command(self, command, commandarg):
        global pod_status
        print("{}: {}".format(command, commandarg))
        command = self.hercules_translator.encode_hercules_command(command, commandarg)
        response = self.xfer16(command)
        print("response: " + str([hex(x) for x in response]))
        pod_status = self.hercules_translator.decode_status_response(response)
        return pod_status

    def BRAKE(self):
        print("THE POD IS BRAKINNGG!!")
        gpio.output(self.brake_pin, False)


class hercules_decoder:
    def __init__(self):
        self.decode_commandargs = lambda x: [(x >> 8), x & 255]

    def decode_status_response(self, response):
        global pod_status
        decoded_status = {}
        decoded_status[PREFIX_MC]= response[0]
        decoded_status[POD_STATE_MC]= HERCULES_STATES[response[1]] if response[1] in HERCULES_STATES else "undefined"
        decoded_status[POD_SUBSTATE_MC]= HERCULES_SUB_STATES[response[2]] if response[2] in HERCULES_SUB_STATES else "undefined"
        decoded_status[ERROR_MC]= HERCULES_ERROR_CODES[response[3]] if response[3] in HERCULES_ERROR_CODES else "undefined"
        decoded_status[ERROR_ARGUMENT_MC] = response[4]
        decoded_status[TIMER_MC]= response[5]
        decoded_status[TARGETSPEED_MC] = response[6]
        decoded_status[BRAKEPOINT_MC] = response[7]
        return decoded_status

    def decode_data_response(self, response):
        pass

    def encode_hercules_command(self, command, commandarg):
        return [MASTER_PREFIX,
                STATE_TRANSITION_COMMANDS[command],
                self.decode_commandargs(commandarg)] + SPI_DATA_TAIL


class logging_messenger(abstract_messenger):
    def __init__(self, logging_frequency=10):
        super(logging_messenger, self).__init__(logging_frequency)
        self.logger = logging.getLogger('pi_sensor_logger')
        hdlr = logging.FileHandler('logs/log_test.log')
        hdlr.setFormatter(logging.Formatter('%(asctime)s: %(message)s'))
        self.logger.addHandler(hdlr)
        self.logger.setLevel(logging.INFO)

    def log_data(self, data):
        if self.time_for_sending_data():
            self.logger.info(data)
            self.reset_last_sent_timer()

class dummy_hercules():
    def __init__(self):
        pass

    def BRAKE(self):
        print("Disconnected! The pod is BRAKING!!!!")

    def send_command(self, command):
        print("Sending command: {}".format(command))
