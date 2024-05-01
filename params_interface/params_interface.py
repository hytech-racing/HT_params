#!/usr/bin/env python
from hytech_eth_np_proto_py import ht_eth_pb2
import socket
import time

def main():
    # Create a config message
    config_msg = ht_eth_pb2.config()
    config_msg.CASE_TORQUE_MAX = -1.0
    config_msg.FRONT_BRAKE_BIAS = 0.7
    config_msg.TCS_ACTIVE = True

    # Wrap the config message in the union
    union_msg = ht_eth_pb2.HT_ETH_Union()
    union_msg.config_.CopyFrom(config_msg)

    # Serialize the message to a string
    data = union_msg.SerializeToString()

    # Define the destination IP address and port
    ip = "192.168.1.30"  # Example IP address
    port = 2000          # Example port number

    # Create a socket and send the data
    while(1):
        # time.sleep(0.1)
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:  # Using UDP for example
            sock.sendto(data, (ip, port))
            print("Message sent!")

if __name__ == "__main__":
    main()