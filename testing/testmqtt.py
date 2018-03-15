# Initialize client and start separate thread for receiving commands
import threading
import paho.mqtt.client as mqtt

def on_connect(self, client, userdata, flags, rc):
    print("Connected to all topics")

def on_message(self, client, userdata, msg):
    print(msg.decode())

client = mqtt.Client("name")
client.on_connect = on_connect
client.on_message = on_message
client.connect("localhost", 1883, 60)
receiver_thread = threading.Thread(target=client.loop_forever)
receiver_thread.start()


data = [1,2,3,4,5]
while True:
    client.publish("data", str(data))
