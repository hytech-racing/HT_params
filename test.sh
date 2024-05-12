#!/bin/bash

# const uint16_t default_protobuf_send_port = 20001;
# const uint16_t default_protobuf_recv_port = 20000;

python3 params_interface/params_interface.py --port 8001 --ip 192.168.1.30 --host_ip 192.168.1.68 --send_port 20000 --recv_port 20001