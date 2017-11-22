import paho.mqtt.client as mqtt
import time
# from test_scripts import Gpio
# gpio = Gpio()

"""
The pod state indicates the state of the pod.
0: Disconnected: Pod is disconnected and waiting to establish connection with
                 the mission control.
1: Connected: Pod is connnected and waiting for commands
2: Running: The pod is running or braking
3: Check: The pod is performing system checks/tests
"""
pod_state = 0


current_time_millis = lambda: time.time()*1000
data_topic = "data"
command_topic = "mc/command"
heartbeat_topic = "mc/heartbeat"
heartbeat_timeout = 1500
last_heartbeat = current_time_millis()

def on_connect(client, userdata, flags, rc):
    # Does not connect to 'data' to prevent recieving duplicate data
    client.subscribe(command_topic)
    client.subscribe(heartbeat_topic)

def on_message(clients, userdata, msg):
    global last_heartbeat, pod_state
    last_heartbeat = current_time_millis()
    pod_state = 1
    if (msg.topic==command_topic):
        handle_commands(msg.payload.decode())

def on_publish(client,userdata, mid):
    pass

def handle_commands(command):
    global client, pod_state
    if command == "start":
        pod_state = 2
        print("Pod has started")
    elif command == "brake":
        print("Pod has braked")
        pod_state = 1
    elif command == "check":
        pod_state = 3
        print("Performing system check")
        pod_state = 1

def is_MC_alive():
    global client, heartbeat_timeout, pod_state, last_heartbeat
    heartbeat_exceeded = (current_time_millis()-last_heartbeat) > heartbeat_timeout*1.5
    if (heartbeat_exceeded and pod_state!=0):
        print("MC is disconnected, the pod braked")
        pod_state = 0
        return False
    if (pod_state==0):
        print("Trying to reconnect with state: {}".format(pod_state), end="\r")
        return False
    return True

client = mqtt.Client("Communication Hubb")
client.on_connect = on_connect
client.connect("localhost", 1883, 60)
client.on_message = on_message
client.on_publish = on_publish
client.loop_start()

run, count = True, 0
while run:
    if is_MC_alive():
        # TODO: read data from the sensors...
        client.publish(data_topic, "Testing script: {}".format(count))
        # TODO: Log data to SD card...
        time.sleep(1)
        count += 1
