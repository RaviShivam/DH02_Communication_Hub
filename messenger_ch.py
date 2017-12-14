import logging
import socket
import threading
import time
import json
from queue import Queue
import RPi.GPIO as gpio

import spidev
from mission_configs import *


spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = SPI_FREQUENCY_HERCULES

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
        self.COMMAND_BUFFER = Queue()

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
                self.COMMAND_BUFFER.put((message[0], int(message[1])))

    def send_data(self, data):
        if self.time_for_sending_data():
            self.client.publish(self.data_topic, payload=json.dumps(data), qos=0)
            self.reset_last_sent_timer()

    def try_to_reconnect(self):
        global pod_state
        if pod_state is "acceleration": mc_messenger.TRIGGER_EMERGENCY_BRAKE()
        while True:
            print("Trying to reconnect")
            time.sleep(0.5)
            if mc_messenger.is_mc_alive():
                break
        if not gpio.output(BRAKE_PIN): gpio.output(BRAKE_PIN, gpio.HIGH)

    def TRIGGER_EMERGENCY_BRAKE(self):
        print("THE POD IS BRAKINNGG!!")
        gpio.output(BRAKE_PIN, gpio.LOW)


class spi16bit:
    def xfer16(self, data, cs_config):
        response = []
        for packet in data:
            [gpio.output(x[0], x[1]) for x in cs_config]
            response.append(spi.xfer(packet))
            self.reset_CS_state()
        processed = [(i[0] << 8) + i[1] for i in response]
        return processed

    def reset_CS_state(self):
        [gpio.output(pin, True) for pin in ALL_CS]



class hercules_comm_module(temporal_messenger, spi16bit):
    def __init__(self, retrieving_frequency, request_packet, comm_config):
        super(hercules_comm_module, self).__init__(sending_frequency=retrieving_frequency)
        self.latest_data = None
        self.has_new_data = False
        self.request_packet = request_packet
        self.comm_config = comm_config

    def request_data(self):
        if self.time_for_sending_data():
            self.latest_data = self.xfer16(self.request_packet, self.comm_config)
            self.has_new_data = True
            self.reset_last_sent_timer()
        return self.latest_data

class hercules_messenger(spi16bit):
    def __init__(self, data_modules, command_config):
        super(hercules_messenger, self).__init__()
        self.data_modules = data_modules
        self.command_config = command_config
        self.decode_commandargs = lambda x: [(x >> 8), x & 255]

    def retrieve_data(self):
        retrieved_data = []
        for module in self.data_modules:
            retrieved_data.append(module.request_data())
        return retrieved_data

    def send_command(self, command, commandarg):
        print((command, commandarg))
        command = self.encode_hercules_command(command, commandarg)
        self.xfer16(command, self.command_config)


    def encode_hercules_command(self, command, commandarg):
        return [MASTER_PREFIX,
                STATE_TRANSITION_COMMANDS[command],
                self.decode_commandargs(commandarg)]


"""
This class is responsible for preparing the data for sending to both SpaceX and the Hyperloop Mission Control. 
"""
class data_segmentor:
    def __init__(self):
        self.latest_mc_data = {}

    def segment_mc_data(self, fullresponse):
        global pod_state
        if fullresponse[0] is None:
            return "undefined"
        low_frequency_response = fullresponse[0]
        high_frequency_response = fullresponse[1]
        decoded_status = {}
        decoded_status[POD_STATE_MC] = HERCULES_STATES[low_frequency_response[1]] if low_frequency_response[
                                                                                         1] in HERCULES_STATES else "undefined"
        decoded_status[POD_SUBSTATE_MC] = HERCULES_SUB_STATES[low_frequency_response[2]] if low_frequency_response[
                                                                                                2] in HERCULES_SUB_STATES else "undefined"
        decoded_status[ERROR_MC] = HERCULES_ERROR_CODES[low_frequency_response[3]] if low_frequency_response[
                                                                                          3] in HERCULES_ERROR_CODES else "undefined"
        decoded_status[ERROR_ARGUMENT_MC] = low_frequency_response[4]
        decoded_status[TIMER_MC] = low_frequency_response[5]
        decoded_status[TARGETSPEED_MC] = low_frequency_response[6]
        decoded_status[BRAKEPOINT_MC] = low_frequency_response[7]
        pod_state = decoded_status[POD_STATE_MC]
        return decoded_status


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


class dummy_hercules():
    def __init__(self):
        pass

    def BRAKE(self):
        print("Disconnected! The pod is BRAKING!!!!")

    def send_command(self, command):
        print("Sending command: {}".format(command))
