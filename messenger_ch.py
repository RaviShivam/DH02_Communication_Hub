import logging
import socket
import threading
import time

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

class temporal_messenger:
    def __init__(self, sending_frequency):
        self.current_time_millis = lambda: time.time() * MILLIS
        self.action_timeout = MILLIS / float(sending_frequency)
        self.last_action = self.current_time_millis()

    def time_for_sending_data(self):
        last_sent_exceeded = (self.current_time_millis() - self.last_action) > self.action_timeout
        return last_sent_exceeded

    def reset_last_sent_timer(self):
        self.last_action = self.current_time_millis()


class spi16bit:
    def xfer16(self, data):
        response = [self.spi.xfer(packet) for packet in data]
        processed = list()
        for i in response:
            processed.append((i[0] << 8) + i[1])
        return processed


class mission_logger:
    def __init__(self, file):
        self.logger = logging.getLogger('pi_sensor_logger')
        hdlr = logging.FileHandler(open(file, 'w'))
        hdlr.setFormatter(logging.Formatter('%(asctime)s: %(message)s'))
        self.logger.addHandler(hdlr)
        self.logger.setLevel(logging.INFO)

    def log_data(self, logging_instance):
        if logging_instance.has_new_data:
            self.logger.info(logging_instance.latest_data)
            logging_instance.has_new_data = False


class mc_messenger(temporal_messenger):
    def __init__(self, client, mc_heartbeat_timeout, sending_frequency=8):
        super(mc_messenger, self).__init__(sending_frequency)
        self.data_topic = DATA_TOPIC
        self.command_topic = COMMAND_TOPIC
        self.heartbeat_topic = HEARTBEAT_TOPIC

        # Heartbeat configurations
        self.heartbeat_timeout = mc_heartbeat_timeout
        self.last_heartbeat = self.current_time_millis()
        self.is_mc_alive = lambda: (self.current_time_millis() - self.last_heartbeat) < self.heartbeat_timeout

        # Initialize client and start separate thread for receiving commands
        self.client = client
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(MQTT_BROKER_ADDRESS, 1883, 60)
        threading.Thread(target=self.client.loop_forever).start()

        # Command buffer will be filled with incoming commands from MC.
        self.COMMAND_BUFFER = []

    def on_connect(self, client, userdata, flags, rc):
        client.subscribe(self.command_topic)
        client.subscribe(self.heartbeat_topic)
        print("Connected to all topics")

    def on_message(self, client, userdata, msg):
        self.last_heartbeat = self.current_time_millis()
        topic, command = msg.topic, msg.payload.decode()
        if topic == self.command_topic:
            if command == EMERGENCY_BRAKE_COMMAND:
                self.TRIGGER_EMERGENCY_BRAKE()
            else:
                message = msg.payload.decode().split(":")
                self.COMMAND_BUFFER.append((message[0], int(message[1])))

    def send_data(self, data):
        if self.time_for_sending_data():
            self.client.publish(self.data_topic, payload=data, qos=0)
            self.reset_last_sent_timer()

    def TRIGGER_EMERGENCY_BRAKE(self):
        print("THE POD IS BRAKINNGG!!")
        gpio.output(BRAKE_PIN, False)


class udp_messenger(temporal_messenger):
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


class hercules_comm_module(temporal_messenger, spi16bit):
    def __init__(self, retrieving_frequency, request_packet, decode, comm_pin):
        super(hercules_comm_module).__init__(retrieving_frequency)
        self.latest_data = None
        self.has_new_data = False
        self.request_packet = request_packet
        self.comm_pin = comm_pin
        self.decode = decode

    def request_data(self):
        if self.time_for_sending_data():
            self.latest_data = self.decode(self.send_command(self.request_packet))
            self.has_new_data = True
            self.reset_last_sent_timer()
        return self.latest_data


class hercules_messenger(spi16bit):
    def __init__(self, data_retrievers, encode):
        self.spi = spidev.SpiDev()
        self.spi.open(0, 0)
        self.spi.max_speed_hz = SPI_FREQUENCY_HERCULES
        self.data_retrievers = data_retrievers
        self.encode = encode

    def retrieve_data(self):
        retrieved_data = []
        for module in self.data_modules:
            retrieved_data.append(module.request_data())
        return retrieved_data

    def send_command(self, command, commandarg):
        command = self.encode(command, commandarg)
        self.xfer16(command)


class hercules_translator:
    """
    This converts a decimal number to 16 bit binary.
    Bit shift the first 8 bits to right and append the last 8 bits.
    """
    def decode_commandargs(self):
        lambda x: [(x >> 8), x & 255]

    def decode_high_frequency_command(self, response):
        pass

    def decode_low_frequency_command(self, response):
        global pod_status
        decoded_status = {}
        decoded_status[PREFIX_MC] = response[0]
        decoded_status[POD_STATE_MC] = HERCULES_STATES[response[1]] if response[1] in HERCULES_STATES else "undefined"
        decoded_status[POD_SUBSTATE_MC] = HERCULES_SUB_STATES[response[2]] if response[
                                                                                  2] in HERCULES_SUB_STATES else "undefined"
        decoded_status[ERROR_MC] = HERCULES_ERROR_CODES[response[3]] if response[
                                                                            3] in HERCULES_ERROR_CODES else "undefined"
        decoded_status[ERROR_ARGUMENT_MC] = response[4]
        decoded_status[TIMER_MC] = response[5]
        decoded_status[TARGETSPEED_MC] = response[6]
        decoded_status[BRAKEPOINT_MC] = response[7]
        return decoded_status

    def encode_hercules_command(self, command, commandarg):
        return [MASTER_PREFIX,
                STATE_TRANSITION_COMMANDS[command],
                self.decode_commandargs(commandarg)]


class dummy_hercules():
    def __init__(self):
        pass

    def BRAKE(self):
        print("Disconnected! The pod is BRAKING!!!!")

    def send_command(self, command):
        print("Sending command: {}".format(command))
