import paho.mqtt.client as mqtt
from messenger_ch import mc_messenger
from messenger_ch import hercules_messenger
from messenger_ch import udp_messenger
from commandhandler_ch import command_handler
import logging
import time
import json

def mc_is_alive(last_heartbeat):
    current_time_millis = lambda: time.time()*1000
    heartbeat_exceeded = (current_time_millis() - last_heartbeat) > heartbeat_timeout*1.5
    return False if heartbeat_exceeded else True

heartbeat_timeout = 1500

client = mqtt.Client("Communication Hub")
hercules_messenger = hercules_messenger(sending_frequency=1)
mc_messenger = mc_messenger(client, hercules_messenger, heartbeat_timeout, sending_frequency=1)
# TODO: spacex_messenger = udp_messenger(client, sending_frequency=2)

run = True
data = "Testing sending."

while run:
    pod_status = hercules_messenger.get_pod_status()
    if mc_is_alive(mc_messenger.last_heartbeat):
        mc_messenger.send_data(json.dumps(pod_status))
    else:
        hercules_messenger.BRAKE()

    # TODO: logger.log(data)
    # TODO: spacex_messenger.send_data(data)
