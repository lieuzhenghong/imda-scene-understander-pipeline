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

def recv_all(msg_len):
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

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_address = ('localhost', 6000)
    sock.bind(server_address)
    sock.listen(1)

    try:
        while True:
            print('waiting for a connection')
            connection, client_address = sock.accept()

            try:
                print(f"Connection from: ", client_address)

                b_msg_len = connection.recv(HEADER_SIZE)
                msg_len = int(b_msg_len.decode("utf-8"))
                print(msg_len)

                # receive the data in small chunks
                full_data = recv_all(msg_len)
                print("All data received!")

                # Now sending the data to the ML model
                print("Sending data to ML model...")
                full_data.seek(0)
                img = np.load(full_data, allow_pickle=True)
                # This is the key: calling the detect function of the model
                bboxes = detect(img, 0.3, 0.4)[0]
                # bboxes is a N x 6 numpy array

                print("Sending data back to the client")
                bbox_bytes = BytesIO()
                np.save(bbox_bytes, bboxes)
                bbox_bytes.seek(0)
                connection.sendall(bbox_bytes.read())

            # Use a try:finally block to close even in the event of an error
            finally:
                connection.close()

    finally:
        print("Closing socket..")
        sock.close()
