import time
import spidev
import RPi.GPIO as gpio
import threading
from hercules_states import state_transition_commands
from hercules_states import hercules_states
from hercules_states import hercules_sub_states
import socket


MILLIS = 1000
pod_status = {"fsmState": "idle", "fsmSubstate": "done"}

class mc_messenger:
    def __init__(self, client, hercules_messenger, mc_heartbeat_timeout, sending_frequency=8):
        self.data_topic = "data"
        self.command_topic = "mc/command"
        self.heartbeat_topic = "mc/heartbeat"

        # Initialize client
        self.client = client
        self.hercules_messenger = hercules_messenger
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect("localhost", 1883, 60)

        self.current_time_millis = lambda: time.time()*MILLIS

        self.last_sent_timeout= MILLIS/float(sending_frequency)
        self.heartbeat_timeout = mc_heartbeat_timeout
        self.last_sent = time.time()*MILLIS
        self.last_heartbeat = time.time()*MILLIS

        t = threading.Thread(target=self.client.loop_forever)
        t.start()
        print("Client service started!")

    def on_connect(self, client, userdata, flags, rc):
        # Does not connect to 'data' to prevent recieving duplicate data
        client.subscribe(self.command_topic)
        client.subscribe(self.heartbeat_topic)
        print("Connected to all topics")

    def on_message(self, client, userdata, msg):
        self.last_heartbeat = self.current_time_millis()
        if (msg.topic==self.command_topic):
            if msg.payload.decode() == "ebrake":
                self.hercules_messenger.BRAKE()
            else:
                self.hercules_messenger.send_command(msg.payload)

    def time_for_sending_data(self):
        last_sent_exceeded = (self.current_time_millis() - self.last_sent) > self.last_sent_timeout
        return last_sent_exceeded

    def send_data(self, data):
        if self.time_for_sending_data():
            self.client.publish(self.data_topic, payload = data, qos= 0)
            self.last_sent = self.current_time_millis()


class hercules_messenger:
    def __init__(self, sending_frequency=4):
        self.brake_pin = 21
        gpio.setmode(gpio.BCM)
        gpio.setup(self.brake_pin, gpio.OUT)
        gpio.output(self.brake_pin, True)

        self.spi = spidev.SpiDev()
        self.spi.open(0, 0)
        self.spi.max_speed_hz = 500000
        self.spi.cshigh = False
        self.spi.mode = 0b00
        self.status_request = [state_transition_commands["get_status"] for _ in range(8)]
        # TODO: add data request

        self.current_time_millis = lambda: time.time()*MILLIS
        self.status_request_timout = MILLIS/float(sending_frequency)
        self.last_status_request = time.time()*MILLIS


    def exchange_data(self, data):
        response = [self.spi.xfer(packet) for packet in data]
        processed = list()
        for i in response:
            processed.append((i[0] << 8) + i[1])
        return processed

    def get_pod_status(self):
        if self.time_for_request():
            response = self.exchange_data(self.status_request)
            self.decode_status_response(response)
            self.last_status_request = self.current_time_millis()
        return pod_status

    def send_command(self, command):
        command = command.decode()
        command = state_transition_commands[command]
        command = [command for _ in range(8)]
        response = self.exchange_data(command)
        self.decode_status_response(response)

    def time_for_request(self):
        last_sent_exceeded = (self.current_time_millis() - self.last_status_request) > self.status_request_timout
        return last_sent_exceeded

    def decode_status_response(self, response):
        print(response)
        if response[1] in hercules_states: 
            pod_status["fsmState"] = hercules_states[response[1]]
        else:
            pod_status["fsmState"] = "undefined"
        if response[2] in hercules_states: 
            pod_status["fsmSubstate"] = hercules_sub_states[response[2]]
        else:
            pod_status["fsmSubstate"] = "undefined"


    def BRAKE(self):
        print("BRAKINNGG")
        gpio.output(self.brake_pin, False)
        time.sleep(5)
        gpio.output(self.brake_pin, True)

class udp_messenger:
    def __init__(self, ip_adress="192.168.0.1", port=3000, sending_frequency=10):
        self.TARGET_IP = ip_adress
        self.TARGET_PORT = port
        self.sending_frequency = sending_frequency
        self.sock = socket.socket(socket.AF_INET,
                             socket.SOCK_DGRAM)

    def send_data(self, data):
        self.sock.sendto(data, (self.TARGET_IP, self.TARGET_PORT))
