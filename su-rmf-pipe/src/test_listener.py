import sys
from unittest.mock import MagicMock
import numpy as np
import pytest
import struct

mockDetector = MagicMock()
mockDetector.return_value = ['fish', 'cow']
print(mockDetector())

sys.modules['B1_detect'] = MagicMock()
sys.modules['B1_detect.detect'] = mockDetector
import recv_stream_and_send_to_model as listener

import time
import multiprocessing

def test_listener():
    '''
    Full integration test.
    Spin up the server as a thread.
    Mock B1_detect.detect function.
    Connect to the server.
    Then send a request to it using create_message_from_np_array
    Check if it:
    1. parses the incoming data correctly,
    2. calls the mockDetector,
    3. returns the correct result
    '''
    import send_cam_stream
    server = multiprocessing.Process(target=listener.main)
    server.start()

    server_addr = ('localhost', 6000)
    img = np.random.rand(640, 480, 3)
    bboxes = send_cam_stream.send_image_to_server(img, server_addr)
    print(bboxes)

    server.terminate()
    server.join()
    print(bboxes)
    print([])


def test_listener_one_object():
    import send_cam_stream
    server = multiprocessing.Process(target=listener.main)
    server.start()

    server_addr = ('localhost', 6000)
    img = np.random.rand(640, 480, 3)
    bboxes = send_cam_stream.send_image_to_server(img, server_addr)
    print(bboxes)

    server.terminate()
    server.join()
    assert(bboxes == [[1,1,1,1,1,1]])



# ROS 2 will send (to server SUM):
# - device id
# - time t (unix time) <-- we might have to publish time to not get stale info
# - location of robot at time t
# - List[x, y, class] at time t

# * 10 bytes [ data  ---------------*-->] * 10 bytes [data --------------->]