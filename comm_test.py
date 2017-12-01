from mission_configs import state_commands
from mission_configs import hercules_states
import paho.mqtt.client as mqtt
import RPi.GPIO as gpio 
import time, spidev, random
import random


brake_pin = 21
gpio.setmode(gpio.BCM)
gpio.setup(brake_pin, gpio.OUT)
gpio.output(brake_pin, True)

spi = spidev.SpiDev()
spi.open(0, 0)

spi.max_speed_hz = 500000
spi.cshigh = False
spi.mode = 0b00

def send_spi_data(data):
    response = [spi.xfer(data) for i in range(8)]
    processed = list()
    for i in response:
        processed.append(hex((i[0] << 8) + i[1]))
    if processed[2] in hercules_states:
        state = hercules_states[processed[2]]
        client.publish("state", state)
    
current_time_millis = lambda: time.time()*1000
data_topic = "data" 
command_topic = "mc/command" 
heartbeat_topic = "mc/heartbeat" 

heartbeat_timeout = 1500
last_heartbeat = current_time_millis()

def on_connect(client, userdata, flags, rc):
    client.subscribe(command_topic)
    client.subscribe(heartbeat_topic)

def on_message(clients, userdata, msg):
    global last_heartbeat
    if (msg.topic==heartbeat_topic):
        last_heartbeat = current_time_millis()
    if (msg.topic==command_topic):
        last_heartbeat = current_time_millis()
        handle_commands(msg.payload.decode())

def brake_pod():
    print("Pod is braking")
    gpio.output(brake_pin, False)

def handle_commands(command):
    global client
    if command=="brake":
        brake_pod()
        return
    if command in state_commands:
        send_spi_data(state_commands[command])

def check_MC_alive():
    global client, heartbeat_timeout, last_heartbeat
    if (current_time_millis() - last_heartbeat > heartbeat_timeout):
        return 0
    return 1

client = mqtt.Client()
client.on_connect = on_connect
client.connect("localhost", 1883, 60)
client.on_message = on_message

#client.publish("data", "Testing script: {}".format(count))
run, count = True, 1

try:
    while run:
        send_spi_data(state_commands["heartbeat"])
        client.loop()
        if (check_MC_alive() == 0): 
            brake_pod()
            break
        client.publish("data", "hearbeat: {}".format(count))
        time.sleep(0.5)
        count += 1
except KeyboardInterrupt:
    gpio.output(brake_pin, False)
    gpio.cleanup()

gpio.output(brake_pin, False)
print("MC was disconnected")
