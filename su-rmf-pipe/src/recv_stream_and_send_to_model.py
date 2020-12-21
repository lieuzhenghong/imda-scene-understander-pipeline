'''
=== TCP server code ===
Sets up a listener on port 6000 and waits for a datastream.
Receives the data from the client (a serialised numpy array),
passes it to James's `detect` function in B1_detect.py
and returns the results.
'''

import socket
import sys
from io import BytesIO
import numpy as np

from B1_detect import detect

HEADER_SIZE = 10

def recv_all(msg_len, connection):
    '''
    Receives data of msg_len in chunks of 4096 bits
    and returns a BytesIO filled with that data
    '''
    full_data = BytesIO()
    while (full_data.getbuffer().nbytes < msg_len):
        data = connection.recv(4096)
        full_data.write(data)
    full_data.seek(0)
    return full_data

from typing import Tuple

def call_detect_function_and_recv_result(b_full_data) -> BytesIO:
    # Now sending the data to the ML model
    print("Sending data to ML model...")
    b_full_data.seek(0)
    img = np.load(b_full_data, allow_pickle=True)
    bboxes = detect(img, 0.3, 0.4)[0]
    # bboxes is a N x 6 numpy array
    print(bboxes)

    print("Sending data back to the client")
    bbox_bytes = BytesIO()
    np.save(bbox_bytes, bboxes)
    bbox_bytes.seek(0)
    return bbox_bytes


class Listener:
    def __init__(self, server_addr: Tuple[str, int], 
                handle_data_fn
                ):
        self.server_addr = server_addr
        self.handle_data_fn = handle_data_fn
    def decode_message(self, connection) -> BytesIO:
        b_msg_len = connection.recv(HEADER_SIZE)
        msg_len = int(b_msg_len.decode("utf-8"))
        print(msg_len)
        # receive the data in small chunks
        full_data = recv_all(msg_len, connection)
        print("All data received!")
        return full_data
    def start_server(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(self.server_addr)
            sock.listen(1)
            try:
                while True:
                    print('waiting for a connection')
                    connection, client_address = sock.accept()
                    try:
                        print(f"Connection from: ", client_address)

                        b_full_data = self.decode_message(connection)
                        b_return_data = self.handle_data_fn(b_full_data)

                        connection.sendall(b_return_data.read())

                    # Use a try:finally block to close even in the event of an error
                    finally:
                        connection.close()
            finally:
                print("Closing socket..")
            sock.close()

def main():
    ml_listener = Listener(("localhost", 6000), call_detect_function_and_recv_result)
    ml_listener.start_server()