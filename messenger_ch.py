import RPi.GPIO as gpio
import json
import logging
import socket
import spidev
import threading
import time
import struct
import paho.mqtt.client as mqtt
from queue import Queue
from threading import Thread

from mission_configs import *

"""
Initialize the spidev module used to communicate with the Hercules board
"""
spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = SPI_FREQUENCY_HERCULES

class temporal_messenger:
    """
    The basic interface implemented by all messengers in used during the mission.
    This class allow the temporal sending of messages, giving all classes extending this class the ability to send messages
    at a specific frequency
    """

    def __init__(self, sending_frequency):
        """
        Initializes the counters for keeping the frequency in check.
        :param sending_frequency: Frequency at which the messenger should operate.
        """
        self.current_time_millis = lambda: time.time() * MILLIS
        self.action_timeout = MILLIS / float(sending_frequency)
        self.last_action = self.current_time_millis()

    def time_for_sending_data(self):
        """
        Checks if the timeout was exceeded.
        :return: True if the messenger can send a new message, False otherwise
        """
        last_sent_exceeded = (self.current_time_millis() - self.last_action) > self.action_timeout
        return last_sent_exceeded

    def reset_last_action_timer(self):
        """
        Resets the timer to the current timestamp.
        :return: None
        """
        self.last_action = self.current_time_millis()


class mission_logger:
    def __init__(self, logger_name, file):
        self.logger = logging.getLogger(logger_name)
        open(file, 'w')
        hdlr = logging.FileHandler(file)
        hdlr.setFormatter(logging.Formatter('%(asctime)s: %(message)s'))
        self.logger.addHandler(hdlr)
        self.logger.setLevel(logging.INFO)

    def log_data(self, logging_instance):
        if logging_instance.has_new_data:
            self.logger.info(logging_instance.latest_data)
            logging_instance.has_new_data = False


class mc_messenger(temporal_messenger):
    """
    Responsible for handling all communication with the mission control. This includes sending data and receiving command
    from the mission control, but also reconnecting and triggering emergency brake if applicable.
    """

    def __init__(self, broker_ip, broker_port, mc_heartbeat_timeout, sending_frequency, segmentor):
        """
        Intializes the MQTT client which is responsible for receiving messages from the mission control.
        :param client: The initialized client MQTT client
        :param mc_heartbeat_timeout: The timeout for heartbeat from the mission control (which checks if the mission control is functional)
        :param sending_frequency: The frequency at which the pod will send sensor data to the mission control.
        """
        super(mc_messenger, self).__init__(sending_frequency)
        self.segment_data = segmentor
        self.data_topic = DATA_TOPIC
        self.command_topic = COMMAND_TOPIC
        self.heartbeat_topic = HEARTBEAT_TOPIC

        # Heartbeat configurations
        self.heartbeat_timeout = mc_heartbeat_timeout
        self.last_heartbeat = self.current_time_millis()
        self.is_mc_alive = lambda: (self.current_time_millis() - self.last_heartbeat) < self.heartbeat_timeout

        # Initialize client and start separate thread for receiving commands
        self.client = mqtt.Client(MQTT_CLIENT_NAME)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(broker_ip, broker_port, 60)
        self.receiver_thread = threading.Thread(target=self.client.loop_forever)
        self.receiver_thread.start()

        # Command buffer will be filled with incoming commands from MC.
        self.COMMAND_BUFFER = Queue()

        # Any to 16 bit converter. Does not handle overflow
        self.int2bits16 = lambda x: [(x >> 8), x & 255]

    def is_int(self, num):
        try:
            int(num)
        except ValueError:
            return False
        return True

    def on_connect(self, client, userdata, flags, rc):
        """
        Callback called when the connect function is called. Here all the client connects to all the necessary topics.
        :param client: The MQTT client.
        :param userdata: Data retrieved from the MQTT network loop
        :param rc: Response code
        :return: None
        """
        client.subscribe(self.command_topic)
        client.subscribe(self.heartbeat_topic)
        print("Connected to all topics")

    def on_message(self, client, userdata, msg):
        """
        Callback triggered when the client receives a message.
        Here, the heartbeat timer is reset and, if applicable, the command buffer is filled with new command from the mc.
        :param client: MQTT client
        :param userdata: data from the MQTT network loop
        :param msg: msg received from the mission control.
        :return: None
        """
        self.last_heartbeat = self.current_time_millis()
        topic, command = msg.topic, msg.payload.decode()
        if topic == self.command_topic:
            state_switch = int(command.split(",")[0][1:])
            if state_switch == EMERGENCY_BRAKE_COMMAND:
                self.TRIGGER_EMERGENCY_BRAKE()
            else:
                message = self.decode(msg.payload)
                self.COMMAND_BUFFER.put(message)

    def decode(self, message):
        message = message.decode()[1:-1].split(",")
        if not all(self.is_int(item) for item in message):
            message = [99, 99]
        message = [self.int2bits16(int(x)) for x in message]
        return message

    def send_data(self, data):
        """
        Sends data to the mission control if the timeout is exceeded.
        The timeout is checked through the temporal messenger interface.
        :param data: Data sent to the mission control.
        :return: None
        """
        if self.time_for_sending_data():
            if data[0] is None:
                return None
            data = self.segment_data(data)
            self.client.publish(self.data_topic, data, qos=0)
            self.reset_last_action_timer()

    def TRIGGER_EMERGENCY_BRAKE(self):
        """
        Triggers the emergency brake by setting BRAKE_PIN low for 1 second.
        This is done on a seperate thread to avoid main thread falling asleep.
        :return: None
        """
        def trigger():
            gpio.output(BRAKE_PIN, gpio.LOW)
            time.sleep(1)
            gpio.output(BRAKE_PIN, gpio.HIGH)

        t = Thread(target=trigger)
        t.start()



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
            self.reset_last_action_timer()
        return self.latest_data


class hercules_messenger(spi16bit):
    def __init__(self, data_modules, command_config):
        super(hercules_messenger, self).__init__()
        self.latest_retrieved_data = []
        self.data_modules = data_modules
        self.command_config = command_config
        self.int2bits16 = lambda x: [(x >> 8), x & 255]

    def poll_latest_data(self):
        new_data = []
        for module in self.data_modules:
            new_data.append(module.request_data())
        self.latest_retrieved_data = new_data

    def send_command(self, command):
        command = [MASTER_PREFIX] + command
        self.xfer16(command, self.command_config)


class data_segmentor:
    """
    This class is responsible for preparing the data for sending to both SpaceX and the Hyperloop Mission Control.
    """
    def SEGMENT_MC_DATA(fullresponse):
        return str(fullresponse)

    def SEGMENT_SPACEX_DATA(fullresponse):
        data = []
        data.append(TEAM_ID)
        if fullresponse[INDEX_POD_STATE] in SPACEX_POD_STATE:
            data.append(SPACEX_POD_STATE[fullresponse[INDEX_POD_STATE]])
        else:
            data.append(1)
        data.append(fullresponse[INDEX_ACCELARATION])
        data.append(fullresponse[INDEX_POSITION])
        data.append(fullresponse[INDEX_VELOCITY])
        data.append(fullresponse[INDEX_BATTERY_VOLTAGE])
        data.append(fullresponse[INDEX_BATTERY_CURRENT])
        data.append(fullresponse[INDEX_BATTERY_TEMPERATURE])
        data.append(fullresponse[INDEX_POD_TEMPERATURE])
        data.append(fullresponse[INDEX_STRIPE_COUNT])
        packer = struct.Struct('>BBlllllllL')
        return packer.pack(*data)

class udp_messenger(temporal_messenger):
    def __init__(self, ip_adress, port, sending_frequency, segment_data):
        super(udp_messenger, self).__init__(sending_frequency)
        self.TARGET_IP = ip_adress
        self.TARGET_PORT = port
        self.segment_data = segment_data
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send_data(self, data):
        if self.time_for_sending_data():
            if len(fullresponse) < 125:
                return None
            data = self.segment_data(data)
            self.sock.sendto(data, (self.TARGET_IP, self.TARGET_PORT))
            self.reset_last_action_timer()
