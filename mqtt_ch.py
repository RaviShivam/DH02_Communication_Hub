import paho.mqtt.client as mqtt
import time
import threading
import json
import random

class Mqtt():
    def __init__(self):
        self.client = mqtt.Client()
        self.readChannel = 'communit'
        self.writeChannel = 'mcontrol'
        self.counter = 1
        print('init')

    def start(self):
        print('start')
        self.client.connect('localhost', 1883, 60)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.sendDemoMsgs()
        self.client.loop_forever()

    def on_connect(self, client, userdata, flags, rc):
        print("Connected")
        self.client.subscribe(self.readChannel)

    def threadFunc(self):
        while True:
            self.client.publish(self.writeChannel, payload=str(json.dumps({
                'fsmState': 'check_a',
                'podSpeed': int(390 + 30 * random.random()),
                'testBool': False
            })))
            time.sleep(0.5)

    def sendDemoMsgs(self):
        t = threading.Thread(target=self.threadFunc)
        t.start()

if __name__ == '__main__':
    print('This file is used with main.py')
