#!/usr/bin/env python

import socket
from hytech_eth_np_proto_py import ht_eth_pb2
import select
import time
def start_udp_server(ip, port, send_port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((ip, port))
    send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print(f"UDP server listening on {ip}:{port}")
    current_config = ht_eth_pb2.config()
    try:
        while True:
            ready = select.select([server_socket], [], [])
            if ready[0]:
                data, addr = server_socket.recvfrom(1024)
                print(f"Received message from {addr}")

                try:
                    union_msg = ht_eth_pb2.HT_ETH_Union()
                    union_msg.ParseFromString(data)
                    
                    if union_msg.HasField('get_config_'):
                        
                        send_sock.sendto(current_config.SerializeToString(), ('192.168.1.69', send_port))
                        print(f"Sent config response to {addr}")
                    else:
                        print("receiving config")
                        current_config = union_msg.config_
                except Exception as e:
                    print(f"Error processing message: {e}")
    finally:
        server_socket.close()
        send_sock.close()

if __name__ == "__main__":
    start_udp_server('192.168.1.12', 2001, 2002)  # Use the correct IP and port