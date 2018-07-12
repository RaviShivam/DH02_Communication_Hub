import logging
import socket
import spidev
import threading
import time
import struct
import multiprocessing

import RPi.GPIO as gpio
import paho.mqtt.client as mqtt

from queue import Queue
from threading import Thread
from multiprocessing import Process
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
    def __init__(self, logger_name, file, handle_data):
        # Setup identity
        self.name = logger_name
        self.handle_data = handle_data
        self.queue = multiprocessing.Queue(-1)

        # Setup logger
        self.logger = logging.getLogger(logger_name)
        file = file + "-" + time.strftime("%Y_%m_%d-%H_%M_%S")
        open(file, 'w')
        hdlr = logging.FileHandler(file)
        hdlr.setFormatter(logging.Formatter('%(asctime)s: %(message)s'))
        self.logger.addHandler(hdlr)
        self.logger.setLevel(logging.INFO)

        logging_process = Process(target=self.logging_process, args=(self.queue,))
        logging_process.start()

    def logging_process(self, queue):
        while True:
            if not queue.empty():
                log_data = self.handle_data(queue.get())
                self.logger.info(log_data)


class mc_messenger():
    """
    Responsible for handling all communication with the mission control. This includes sending data and receiving command
    from the mission control, but also reconnecting and triggering emergency brake if applicable.
    """

    def __init__(self, broker_ip, broker_port, mc_heartbeat_timeout, high_frequency, low_frequency, handle_data):
        """
        Intializes the MQTT client which is responsible for receiving messages from the mission control.
        :param client: The initialized client MQTT client
        :param mc_heartbeat_timeout: The timeout for heartbeat from the mission control (which checks if the mission control is functional)
        :param sending_frequency: The frequency at which the pod will send sensor data to the mission control.
        """
        self.handle_data = handle_data
        self.low_data_topic = LOW_DATA_TOPIC
        self.high_data_topic = HIGH_DATA_TOPIC
        self.command_topic = COMMAND_TOPIC
        self.heartbeat_topic = HEARTBEAT_TOPIC

        # Check for sending frequencies
        self.lowf_messenger = temporal_messenger(low_frequency)
        self.highf_messenger = temporal_messenger(high_frequency)

        # Heartbeat configurations
        self.current_time_millis = lambda: time.time() * MILLIS
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

    def isint(self, x):
        try:
            int(x)
            return True
        except ValueError:
            return False

    def on_connect(self, client, userdata, flags, rc):
        """
        Callback called when the connect function is called. Here all the client connects to all the necessary topics.
        :param client: The MQTT client.
        :param userdata: Data retrieved from the MQTT network loop
        :param rc: Response code
        :return: None
        """
        print("Initialize messenger")
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
            state_switch, arg1, arg2 = self.sanity_check(command.split(","))
            # Immediate trigger brake (no queue needed)
            if state_switch == EMERGENCY_BRAKE_COMMAND:
                self.TRIGGER_EMERGENCY_BRAKE()
                print("Pod Stop Command issued")
            else:
                self.COMMAND_BUFFER.put([state_switch, arg1, arg2])

    def sanity_check(self, message):
        if len(message) != 3 or not all(self.isint(item) for item in message):
            message = [404, 404, 404]
        message = [int(x) for x in message]
        return message

    def send_data(self, data):
        """
        Sends data to the mission control if the timeout is exceeded.
        The timeout is checked through the temporal messenger interface.
        :param data: Data sent to the mission control.
        :return: None
        """
        if data[0] is None or data[1] is None:
            return None
        low_data, high_data = self.handle_data(data)
        if self.lowf_messenger.time_for_sending_data():
            self.client.publish(self.low_data_topic, low_data, qos=0)
            self.lowf_messenger.reset_last_action_timer()

        if self.highf_messenger.time_for_sending_data():
            self.client.publish(self.high_data_topic, high_data, qos=0)
            self.highf_messenger.reset_last_action_timer()

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
    def __init__(self, retrieving_frequency, request_packet, comm_config, handle_data, logger=None):
        super(hercules_comm_module, self).__init__(sending_frequency=retrieving_frequency)
        self.latest_data = None
        self.request_packet = request_packet
        self.comm_config = comm_config
        self.handle_data = handle_data
        self.logger = logger

    def request_data(self):
        if self.time_for_sending_data():
            raw_data = self.xfer16(self.request_packet, self.comm_config)
            self.latest_data = self.handle_data(raw_data)
            self.logger.queue.put(self.latest_data)
            self.reset_last_action_timer()
        return self.latest_data


class hercules_messenger(spi16bit):
    def __init__(self, data_modules, command_config):
        super(hercules_messenger, self).__init__()
        self.latest_retrieved_data = []
        self.data_modules = data_modules
        self.command_config = command_config
        # Any to 16 bit converter. Does not handle overflow
        self.int2bits16 = lambda x: [(x >> 8), x & 255]

    def poll_latest_data(self):
        new_data = []
        for module in self.data_modules:
            new_data.append(module.request_data())
        self.latest_retrieved_data = new_data

    def send_command(self, command):
        decoded_command = [self.int2bits16(int(x)) for x in command]
        decoded_command = [MASTER_PREFIX] + decoded_command
        self.xfer16(decoded_command, self.command_config)

    def INITIALIZE_HERCULES(self):
        """
        Trigger resets untill the correct sequence of data is received from the hercules.
        :return : None
        """
        print("(Re)Initializing hercules")
        gpio.output(RESET_PIN, gpio.LOW)
        time.sleep(0.5)
        gpio.output(RESET_PIN, gpio.HIGH)
        c = 0
        while True:
            response_prefix = []
            for _ in range(10):
                self.poll_latest_data()
                # Save received prefixes.
                if self.data_modules[0].latest_data is None:
                    response_prefix.append(0)
                else:
                    response_prefix.append(self.data_modules[0].latest_data[0])
                    response_prefix.append(self.data_modules[1].latest_data[0])
            print("Received reponse: {}".format(response_prefix))
            response_prefix = [x == 0x200 for x in response_prefix]
            if all(response_prefix):
                print("Initialized hercules succesfully!")
                break
            gpio.output(RESET_PIN, gpio.LOW)
            time.sleep(0.5)
            gpio.output(RESET_PIN, gpio.HIGH)

            if c == 20:
                print("Unable to reinitialize hercules")
                break
            time.sleep(0.5)
            c += 1


class udp_messenger(temporal_messenger):
    def __init__(self, ip_adress, port, sending_frequency, handle_data):
        super(udp_messenger, self).__init__(sending_frequency)
        self.TARGET_IP = ip_adress
        self.TARGET_PORT = port
        self.handle_data = handle_data
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send_data(self, data):
        if self.time_for_sending_data():
            if len(data) < 125:
                return None
            data = self.handle_data(data)
            self.sock.sendto(data, (self.TARGET_IP, self.TARGET_PORT))
            self.reset_last_action_timer()
