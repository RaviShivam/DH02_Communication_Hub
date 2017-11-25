"""
This is a simulation script for the mission control.
It performs all the action that are expected to be executed by the mission
control.
"""
import paho.mqtt.client as mqtt
import sys
import time
import threading
import random

current_time_millis = lambda: time.time()*1000

data_topic = "data"
command_topic = "mc/command"
heartbeat_topic = "mc/heartbeat"

def on_connect(client, userdata, flags, rc):
    client.subscribe(data_topic)

def on_message(clients, userdata, msg):
    print(msg.payload.decode())

client = mqtt.Client()
client.on_connect = on_connect
client.connect("localhost", 1883, 60)
client.on_message = on_message

run, count = True, 1
client.loop_start()
while run:
    client.publish(heartbeat_topic, "beep")
    count += 1
    time.sleep(0.5)
