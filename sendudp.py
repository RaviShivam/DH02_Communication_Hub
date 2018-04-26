import struct
import socket
import time


TARGET_IP = "145.94.154.215"
TARGET_PORT = 5005
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

while True:
	data = struct.pack(">10l", *[-i for i in range(10)])
	sock.sendto(data, (TARGET_IP, TARGET_PORT))
	time.sleep(0.5)
