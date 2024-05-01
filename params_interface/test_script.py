#!/usr/bin/env python

import socket
from hytech_eth_np_proto_py import ht_eth_pb2
import select

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

                # Handle incoming message based on protobuf definition
                try:
                    union_msg = ht_eth_pb2.HT_ETH_Union()
                    union_msg.ParseFromString(data)
                    print(union_msg)
                    if union_msg.HasField('get_config_'):
                        union_response = ht_eth_pb2.HT_ETH_Union()
                        union_response.config_.CopyFrom(current_config)
                        send_sock.sendto(union_response.SerializeToString(), (ip, send_port))
                        print(f"Sent config response to {addr}")
                    else:
                        current_config = union_msg.config_
                except Exception as e:
                    print(f"Error processing message: {e}")
    finally:
        server_socket.close()
        send_sock.close()

if __name__ == "__main__":
    start_udp_server('127.0.0.1', 2001, 2002)  # Use the correct IP and port
