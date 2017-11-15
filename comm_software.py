import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
import time
import threading
import random

class Gpio():
    def __init__(self):
        # For GPIO numbering, instead of pin numbering
        GPIO.setmode(GPIO.BCM)

        self.redLed = 21
        self.greenLed = 20

        GPIO.setup(self.redLed, GPIO.OUT)
        GPIO.setup(self.greenLed, GPIO.OUT)
        GPIO.output(self.redLed, False)
        GPIO.output(self.greenLed, False)


    def startPod(self):
        GPIO.output(self.redLed, False)
        GPIO.output(self.greenLed, True)
        print('Pod started')

    def brakePod(self):
        GPIO.output(self.redLed, True)
        GPIO.output(self.greenLed, False)
        print('Pod braked')

    def ledDemo(self):
        for i in range(2):
            GPIO.output(self.redLed, True)
            GPIO.output(self.greenLed, False)
            time.sleep(1)
            GPIO.output(self.redLed, False)
            GPIO.output(self.greenLed, True)
            time.sleep(1)
    def stop():
        GPIO.cleanup()

import time

current_time_millis = lambda: time.time()*1000

gpio = Gpio()
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

def on_publish(client,userdata, mid):
    pass

def handle_commands(command):
    global client
    print(command)
    if command == "start":
        # handle_start_command()
        gpio.startPod()
    elif command == "brake":
        # handle_stop_command()
        gpio.brakePod()
    elif command == "check":
        print("Performing system check")

def check_MC_alive():
    global client, heartbeat_timeout, last_heartbeat
    if (current_time_millis() - last_heartbeat > heartbeat_timeout):
        gpio.brakePod()
        return 0
    return 1

    

client = mqtt.Client()
client.on_connect = on_connect
client.connect("localhost", 1883, 60)
client.on_message = on_message
client.on_publish = on_publish

run, count = True, 0

while run:
    client.loop()
    if (check_MC_alive() == 0): break
    client.publish("data", "Testing script: {}".format(count))
    time.sleep(0.3)
    count += 1

print("MC was disconnected")
