import sys
from unittest.mock import MagicMock
import numpy as np
import pytest
import struct

mockModel = MagicMock()

import time
import multiprocessing
import importlib

import random

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

@pytest.fixture
def init_listener():
    from listener import Listener
    server_addr = ('localhost', 6000)
    server = Listener(server_addr, None)
    return server

def test_recv_header(init_listener):
    '''
    Tests that the recv_header method in the Listener class
    can decode a padded bytestring
    and return the correct integer
    '''
    arbitrary_header_len = 123
    def mockDataStream(size):
        return bytes(str(f"{arbitrary_header_len:<{size}}"), 'utf-8')
    mockConnection = MagicMock()
    mockConnection.recv = mockDataStream

    init_listener.connection = mockConnection
    header_len = init_listener.recv_header()
    assert(header_len == arbitrary_header_len)

def test_recv_all(init_listener):
    '''
    Tests that the recv_all method in the Listener class
    can receive any number of bytes
    and successfully decode it
    '''
    SIZE = 4096
    class MockConnection():
        def __init__(self, size):
            self.left_ptr = 0
            self.arbitrary_data = bytearray(random.getrandbits(8) for _ in range(size)) 
        def recv(self, size):
            r = self.arbitrary_data[self.left_ptr:self.left_ptr+size]
            self.left_ptr += size
            return r

    mockConnection = MockConnection(SIZE)
    init_listener.connection = mockConnection
    full_data = init_listener.recv_all(SIZE)
    assert(full_data.read() == mockConnection.arbitrary_data)