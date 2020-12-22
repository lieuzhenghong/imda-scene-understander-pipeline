import sys
from unittest.mock import MagicMock
import numpy as np
import pytest
import struct

mockModel = MagicMock()

import time
import multiprocessing
import importlib

mockDetector = MagicMock(return_value=[[], []])
mockModel.detect = mockDetector
print(mockModel.detect())
sys.modules['B1_detect'] = mockModel
import recv_stream_and_send_to_model as listener

def test_recv_stream_and_send_to_model_integration():
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
    assert (bboxes.size == 0)

def test_recv_stream_and_send_to_model_one_object():
    '''
    We now change the mockDetector so it returns one object
    Check that our listener can still handle this
    '''
    mockDetector = MagicMock(return_value=[np.ones((1,6)), []])
    mockModel.detect = mockDetector
    importlib.reload(listener)

    import send_cam_stream
    server = multiprocessing.Process(target=listener.main)
    server.start()

    server_addr = ('localhost', 6000)
    img = np.random.rand(640, 480, 3)
    bboxes = send_cam_stream.send_image_to_server(img, server_addr)
    print(bboxes)

    server.terminate()
    server.join()
    assert(bboxes.shape == (1,6))

def test_multiple_recv():
    '''
    Test if the server can handle multiple sequential requests
    '''
    mockDetector = MagicMock(return_value=[np.ones((1,6)), []])
    mockModel.detect = mockDetector
    importlib.reload(listener)

    import send_cam_stream
    server = multiprocessing.Process(target=listener.main)
    server.start()

    server_addr = ('localhost', 6000)
    img = np.random.rand(640, 480, 3)
    bboxes = send_cam_stream.send_image_to_server(img, server_addr)
    print(bboxes)
    bboxes2 = send_cam_stream.send_image_to_server(img, server_addr)
    print(bboxes2)

    server.terminate()
    server.join()
    assert(bboxes.shape == (1,6))
    assert(bboxes2.shape == (1,6))

# ROS 2 will send (to server SUM):
# - device id
# - time t (unix time) <-- we might have to publish time to not get stale info
# - location of robot at time t
# - List[x, y, class] at time t

# * 10 bytes [ data  ---------------*-->] * 10 bytes [data --------------->]