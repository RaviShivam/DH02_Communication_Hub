import json
import paho.mqtt.client as mqtt
from random import random
from mission_configs import *
# from messenger_ch import hercules_messenger
from messenger_ch import dummy_hercules
from messenger_ch import mc_messenger
from messenger_ch import udp_messenger
from messenger_ch import logging_messenger

client = mqtt.Client(MQTT_CLIENT_NAME)
hercules_messenger = dummy_hercules()
mc_messenger = mc_messenger(client, dummy_hercules, HEARTBEAT_TIMEOUT_MC, sending_frequency=SENDING_FREQUENCY_MC)
spacex_messenger = udp_messenger(client, sending_frequency=SENDING_FREQUENCY_SPACEX)
pi_logger = logging_messenger(logging_frequency=LOGGING_FREQUENCY)

run = True
pod_status = 1
states = ["idle", "check_a", "check_b", "check_c", "pumpdown_idle", "ready", "accelaration", "decelaration", "standstill", "shutdown"]
substates = ["none", "busy", "done"]
while run:
    for s in states:
        for sub in substates:
            data = {
                "fsmState": s,
                "fsmSubstate": sub,
                "demoSensor": random()*100
            }
    pi_logger.log_data(data=data)
    if mc_messenger.check_mc_alive():
        mc_messenger.send_data(json.dumps(pod_status))
    else:
        if pod_status is 1:
            dummy_hercules.BRAKE()
        else:
            print("Trying to reconnect")


    # TODO: logger.log(data)
    # TODO: spacex_messenger.send_data(data)
