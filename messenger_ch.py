import time
import spidev
from hercules_states import state_commands
from hercules_states import hercules_states
from hercules_states import hercules_sub_states


MILLIS = 1000

# class abstract_messenger:
#     def __init__(self)

class mc_messenger:
    def __init__(self, client, command_handler, mc_heartbeat_timeout, sending_frequency=8):
        self.data_topic = "data"
        self.command_topic = "mc/command"
        self.heartbeat_topic = "mc/heartbeat"
        self.client = client
        self.command_handler = command_handler
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect("localhost", 1883, 60)
        self.last_sent_timeout= MILLIS/float(sending_frequency)
        self.heartbeat_timeout = mc_heartbeat_timeout
        self.last_sent = time.time()*MILLIS
        self.last_heartbeat = time.time()*MILLIS
        print("Starting MC messenger...")
        #self.client.loop_start()
        self.client.loop_forever()


    def on_connect(self, client, userdata, flags, rc):
        # Does not connect to 'data' to prevent recieving duplicate data
        client.subscribe(self.command_topic)
        client.subscribe(self.heartbeat_topic)
        self.command_handler.pod_state = 1
        print("Connected to all topics")

    def on_message(self, client, userdata, msg):
        self.last_heartbeat = time.time()*1000
        print("Beep...")
        if (msg.topic==self.command_topic):
            self.handle_commands(msg.payload.decode())

    def time_to_send(self):
        current_time_millis = lambda: time.time()*MILLIS
        last_sent_exceeded = (current_time_millis() - self.last_sent) > self.last_sent_timeout*1.5
        return False if last_sent_exceeded else True

    def send_data(self, data):
        if self.time_to_send():
            self.client.publish(self.data_topic, payload = data, qos= 0)
            self.last_sent = time.time()*1000

    def handle_commands(self, command):
        if command == "start":
            self.command_handler.start_pod()
        elif command == "brake":
            self.command_handler.brake_pod()
        elif command == "check":
            self.command_handler.perform_system_check()


class hercules_messenger:
    def __init__(self, sending_frequency=4):
        self.spi = spidev.SpiDev()
        self.spi.open(0, 0)
        self.spi.max_speed_hz = 500000
        self.spi.cshigh = False
        self.spi.mode = 0b00

        def send_data(data):
            response = [self.spi.xfer(data) for i in range(8)]
            processed = list()
            for i in response:
                processed.append(hex((i[0] << 8) + i[1]))
            if processed[2] in hercules_states:
                state = hercules_states[processed[2]]
                client.publish("state", state)

class udp_messenger:
    pass
