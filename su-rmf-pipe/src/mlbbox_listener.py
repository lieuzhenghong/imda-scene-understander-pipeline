"""
=== TCP server code ===
Sets up a listener on port 6000 and waits for a datastream.
Receives the data from the client (a serialised numpy array),
passes it to James's `detect` function in B1_detect.py
and returns the results.
"""

import sys
from io import BytesIO
import numpy as np
from listener import Listener


def call_detect_function_and_recv_result(b_full_data) -> BytesIO:
    from B1_detect import detect

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


def main():
    ml_listener = Listener(("localhost", 6000), call_detect_function_and_recv_result)
    ml_listener.start_server()
