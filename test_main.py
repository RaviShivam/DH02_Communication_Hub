from messenger_ch import udp_messenger
import socket
import time
import mission_configs as constants

# TODO: spacex_messenger = udp_messenger(constants.IP_ADRESS_SPACEX, constants.PORT_SPACEX, constants.SENDING_FREQUENCY_SPACEX)
UDP_IP = "10.42.0.1"
UDP_PORT = 1000 

spacex_messenger = udp_messenger(ip_adress=UDP_IP, port=UDP_PORT, sending_frequency=2)

while True:
    spacex_messenger.send_data(b'Testing UDP')
    time.sleep(0.5)
