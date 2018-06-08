import socket
import struct

UDP_IP = "10.42.0.1"
UDP_PORT = 5005

sock = socket.socket(socket.AF_INET, # Internet
             socket.SOCK_DGRAM) # UDP
sock.bind((UDP_IP, UDP_PORT))

unpacker = struct.Struct(">HHlllllllL")
while True:
    data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
    print "received message:", unpacker.unpack(data)
