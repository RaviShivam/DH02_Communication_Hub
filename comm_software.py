import paho.mqtt.client as mqtt
from messenger_ch import mc_messenger
from messenger_ch import udp_messenger
from commandhandler_ch import command_handler
import logging
import time

def mc_is_alive(last_heartbeat):
    current_time_millis = lambda: time.time()*1000
    heartbeat_exceeded = (current_time_millis() - last_heartbeat) > heartbeat_timeout*1.5
    return False if heartbeat_exceeded else True

"""
The pod state indicates the state of the pod.
0: Disconnected: Pod is disconnected and waiting to establish connection with
                 the mission control.
1: Connected: Pod is connnected and waiting for commands
2: Running: The pod is running or braking
3: Check: The pod is performing system checks/tests
"""
pod_state = 0
heartbeat_timeout = 1500

command_handler = command_handler(pod_state)
client = mqtt.Client("Communication Hub")

mc_messenger = mc_messenger(client, command_handler, heartbeat_timeout, sending_frequency=1)
# TODO: spacex_messenger = udp_messenger(client, sending_frequency=2)
# TODO: hercules_messenger = hercules_messenger()

run = True
data = "Testing sending."

while run:
    if mc_is_alive(mc_messenger.last_heartbeat):
        mc_messenger.send_data(data)
    time.sleep(0.2)
    print("running")
    # TODO: dma_handler.read(data)
    # TODO: logger.log(data)
    # TODO: spacex_messenger.send_data(data)
