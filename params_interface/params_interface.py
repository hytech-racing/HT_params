#!/usr/bin/env python
from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse
import socket
import select
from hytech_eth_np_proto_py import ht_eth_pb2
import threading
import argparse
import sys

class RequestHandler(BaseHTTPRequestHandler):
    config_msg = ht_eth_pb2.config()  # Holds the current or last known configuration
    
    def __init__(self, *args, **kwargs):
        self.ip = kwargs.pop('recv_ip')
        self.host_ip = kwargs.pop('host_ip')
        self.send_port = kwargs.pop('send_port')
        self.recv_port = kwargs.pop('recv_port')
        super().__init__(*args, **kwargs)

    def _send_response(self, html):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))

    def do_GET(self):
        self._send_form(RequestHandler.config_msg, message="")

    def _send_form(self, message_proto, message=''):
        fields_html = self.generate_fields_html(message_proto)
        html = f'''
        <html>
        <body>
            <h2>Configure HT_ETH</h2>
            {message}
            <form action="/" method="post">
                {fields_html}
                <input type="submit" value="Submit">
            </form>
            <form action="/getconfig" method="post">
                <input type="submit" value="Get Config">
            </form>
        </body>
        </html>
        '''
        self._send_response(html)

    def generate_fields_html(self, message_proto):
        fields_html = ""
        for field_desc in message_proto.DESCRIPTOR.fields:
            default_value = getattr(message_proto, field_desc.name)
            if field_desc.type == field_desc.TYPE_BOOL:
                selected_true = 'selected' if default_value else ''
                selected_false = 'selected' if not default_value else ''
                fields_html += f'{field_desc.name}: <select name="{field_desc.name}"><option value="True" {selected_true}>True</option><option value="False" {selected_false}>False</option></select><br>'
            else:
                fields_html += f'{field_desc.name}: <input type="text" name="{field_desc.name}" value="{default_value}"><br>'
        return fields_html

    def do_POST(self):
        if self.path == '/getconfig':
            self.handle_get_config_request()
        else:
            self.handle_update_config_request()

    def handle_update_config_request(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = urllib.parse.parse_qs(post_data.decode('utf-8'))

        config_msg = ht_eth_pb2.config()
        for field_desc in config_msg.DESCRIPTOR.fields:
            field_value = data.get(field_desc.name, [''])[0]
            if field_desc.type == field_desc.TYPE_BOOL:
                setattr(config_msg, field_desc.name, field_value == 'True')
            elif field_desc.type == field_desc.TYPE_FLOAT:
                setattr(config_msg, field_desc.name, float(field_value))
            elif field_desc.type == field_desc.TYPE_INT32:
                setattr(config_msg, field_desc.name, int(field_value))

        RequestHandler.config_msg = config_msg  # Update the last known config

        union_msg = ht_eth_pb2.HT_ETH_Union()
        union_msg.config_.CopyFrom(config_msg)
        print(union_msg)
        serialized_data = union_msg.SerializeToString()

        self.send_udp_message(serialized_data)
        self._send_form(config_msg, '<p><strong>Configuration Updated Successfully</strong></p>')

    def handle_get_config_request(self):
        get_config_msg = ht_eth_pb2.get_config(update_frontend=True)
        union_msg = ht_eth_pb2.HT_ETH_Union()
        union_msg.get_config_.CopyFrom(get_config_msg)
        serialized_data = union_msg.SerializeToString()

        self.send_udp_message(serialized_data)
        # Now wait for response asynchronously or via a separate thread
        response_data, got_resp = self.receive_udp_message()
        if response_data and got_resp:
            print("yo got somethin")
            
            config_union_msg = ht_eth_pb2.HT_ETH_Union()
            config_union_msg.ParseFromString(response_data)
            print(config_union_msg)
            RequestHandler.config_msg = config_union_msg.config_
            self._send_form(RequestHandler.config_msg, '<p><strong>Configuration Received Successfully</strong></p>')
        else:
            print("error, didnt get any response")
            self._send_form(RequestHandler.config_msg, '<p><strong>Error: No response received</strong></p>')

    def send_udp_message(self, data):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            print("sending to ",self.ip)
            print("send port ", self.send_port)
            sock.sendto(data, (self.ip, self.send_port))
            print("Message sent!")

    def receive_udp_message(self, timeout=2):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                print(self.recv_port)
                print(self.host_ip)
                sock.bind((self.host_ip, self.recv_port))
                
                ready = select.select([sock], [], [], timeout)
                print("attempting to recv")
                if ready[0]:
                    print("ready")
                    data, addr = sock.recvfrom(4000)
                    return data, ready[0]
                else:
                    self._send_form(RequestHandler.config_msg, f'<p><strong>Error: {str("rip no msg recvd")}</strong></p>')
                    return bytes(), False
        except OSError as e:
            print(f"Error receiving UDP message: {str(e)}")
            self._send_form(RequestHandler.config_msg, f'<p><strong>Error: {str(e)}</strong></p>')
        return None

def run(send_port, recv_port, host_ip, recv_ip, server_class=HTTPServer, handler_class=RequestHandler, port=8000):
    def handler(*args, **kwargs):
        handler_class(send_port=send_port, recv_port=recv_port, host_ip=host_ip, recv_ip=recv_ip, *args, **kwargs)
    server_address = ('', port)
    httpd = server_class(server_address, handler)
    print(f'Server running on port {port}...')
    httpd.serve_forever()

if __name__ == "__main__":
    send_port = int(sys.argv[1])
    recv_port = int(sys.argv[2])
    web_port = int(sys.argv[3])
    host_ip = sys.argv[4]
    recv_ip = sys.argv[5]
    run(port=web_port, send_port=send_port, recv_port=recv_port, host_ip=host_ip, recv_ip=recv_ip)
