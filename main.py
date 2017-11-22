#!/usr/bin/python3

from gpio_ch import Gpio
from mqtt_ch import Mqtt

print('Python script started')

#gpio = Gpio()
#gpio.start()

def mqtt_on_message(self, client, userdata, msg):
    print('Message received')
    message = msg.payload.decode()
    if message == 'brake':
        print('gpio.brakePod()')
    elif message == 'start':
        print('gpio.startPod()')
    else:
        print('No valid command')
    print("{}: {}".format(msg.topic, message))



mqtt = Mqtt()
setattr(mqtt, 'on_message', mqtt_on_message)
#setattr(mqtt, 'on_connect', mqtt_on_connect)

mqtt.start()
