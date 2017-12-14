import json
import paho.mqtt.client as mqtt
from random import random
from mission_configs import *
# from messenger_ch import hercules_messenger
from messenger_ch import dummy_hercules
from messenger_ch import mc_messenger
from messenger_ch import udp_messenger
from messenger_ch import logging_messenger
import itertools
import time

client = mqtt.Client(MQTT_CLIENT_NAME)
hercules_messenger = dummy_hercules()
mc_messenger = mc_messenger(client, dummy_hercules, HEARTBEAT_TIMEOUT_MC, sending_frequency=SENDING_FREQUENCY_MC)
spacex_messenger = udp_messenger(client, sending_frequency=SENDING_FREQUENCY_SPACEX)
pi_logger = logging_messenger(logging_frequency=LOGGING_FREQUENCY)

run = True
states = ["idle", "check_a", "check_b", "check_c", "pumpdown_idle", "ready", "accelaration", "decelaration", "standstill", "shutdown"]
substates = ["none", "busy", "done"]
combination = itertools.cycle(itertools.product(*[states, substates]))

def try_to_reconnect():
    while True:
        print("Trying to reconnect")
        time.sleep(1)
        if mc_messenger.is_mc_alive():
            break

while run:
    state, substate = next(combination)
    data = {
        "fsmState": state,
        "fsmSubstate": substate,
        "demoSensor": random()*100
    }
    pi_logger.log_data(data=data)
    if mc_messenger.is_mc_alive():
        mc_messenger.send_data(json.dumps(data))
    else:
        hercules_messenger.BRAKE()
        try_to_reconnect()
