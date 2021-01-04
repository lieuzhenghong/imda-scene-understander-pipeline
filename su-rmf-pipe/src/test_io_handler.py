import pyrealsense2 as rs
from unittest.mock import MagicMock, create_autospec
import numpy as np
import pytest
import socket
from io import BytesIO

from typing import List
import send_cam_stream

####################################################
# Mock classes
# Implement mock interfaces for costly objects
# (sockets, RealSense camera, etc.)
###################################################

class MockRealSenseConfig:
    def enable_stream(self, *args):
        # print("\nStream enabled")
        return

class MockRealSensePipeline:
    def start(self, config: MockRealSenseConfig) -> None:
        return "\nOK" 
    def wait_for_frames(self):
        return MockRealSenseFrames()
    def stop(self) -> None:
        return "\nStopped"

class MockRealSenseFrames:
    def get_depth_frame(self):
        return MockRealSenseDepthFrame()
    def get_color_frame(self):
        return MockRealSenseColorFrame()

class MockRealSenseDepthFrame:
    def get_data(self):
        return np.random.rand(640, 480)

class MockRealSenseColorFrame:
    def get_data(self):
        return np.random.rand(640, 480, 3)

'''
class MockServer:
    def __init__(self, num_bboxes, addr=None):
        self.addr = addr
        self.num_bboxes = num_bboxes
        self.bboxes = []
    def receive_connection(self):
        pass
    def generate_bboxes(self):
        if self.num_bboxes:
            self.bboxes = np.random.rand(self.num_bboxes, 6)
    def sendall(self, bbox_bytes):
        return MockServer.generate_message(self.bboxes)
    @staticmethod
    def generate_message(bboxes):
        bbox_bytes = BytesIO()
        np.save(bbox_bytes, bboxes)
        bbox_bytes.seek(0)
        return bbox_bytes
'''

class MockSocket:
    # We need enter and exit methods so that it works with a with block
    def __init__(self, addr=None):
        self.all_data_sent = False 
        self.addr = addr
        self.num_bboxes = 0
        self.bboxes = []
    def __enter__(self):
        return self
    def connect(self, addr):
        self.addr = addr
        return self.addr
    def sendall(self, all_bytes):
        # print(all_bytes)
        print("\nAll bytes sent")
        return
    def recv(self, nbytes: int) -> BytesIO:
        self.__generate_bboxes__()
        bbox_bytes = MockSocket.__generate_message__(self.bboxes)
        if self.all_data_sent:
            return None
        else:
            self.all_data_sent = True
            return bbox_bytes.read()
    def close(self):
        print("\nSocket connection closed")
        return
    def __generate_bboxes__(self):
        if self.num_bboxes:
            self.bboxes = np.random.rand(self.num_bboxes, 6)
    @staticmethod
    def __generate_message__(bboxes):
        bbox_bytes = BytesIO()
        np.save(bbox_bytes, bboxes)
        bbox_bytes.seek(0)
        return bbox_bytes
    def __exit__(self, *args, **kwargs):
        pass

class MockBoundingBox:
    def __init__(self, x1, y1, x2, y2, s, c):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.s = s
        self.c = c

# 
# Monkeypatch library calls to use our mocks 
# 

@pytest.fixture(autouse=True)
def mock_rs(monkeypatch):
    def mock_pipeline(*args, **kwargs):
        return MockRealSensePipeline()

    def mock_config(*args, **kwargs):
        return MockRealSenseConfig()

    monkeypatch.setattr(rs, "pipeline", mock_pipeline)
    monkeypatch.setattr(rs, "config", mock_config)

@pytest.fixture(autouse=True)
def mock_socket(monkeypatch):
    def init_mock_socket(*args, **kwargs):
        return MockSocket()
    
    monkeypatch.setattr(socket, "socket", init_mock_socket)

###############################################################
# TESTS
###############################################################

def test_init_pipeline():
    pipeline = send_cam_stream.init_pipeline()
    assert True

def test_get_frames():
    '''
    Test that we can get depth and color frames 
    and they are of the correct dimensions
    '''
    pipeline = send_cam_stream.init_pipeline()
    depth_frame, color_frame = send_cam_stream.get_frames(pipeline)
    assert (np.shape(depth_frame.get_data()) == (640, 480)) 
    assert np.shape(color_frame.get_data()) == (640, 480, 3)

def test_send_image_to_server():
    '''
    Integration test:
    test that `send_image_to_server`
    succesfully 
    # FIXME don't mock this
    '''
    img = np.random.rand(640, 480, 3)
    server_address = ('localhost', 6000)
    bboxes = send_cam_stream.send_image_to_server(img, server_address)
    assert np.size(bboxes) == 0

def test_create_message_messageIsWellFormed():
    '''
    Tests that `create_message_from_np_array`
    creates a well-formed message with a 10-byte long header
    (with correct message size)
    and correctly encodes the numpy array
    '''
    HEADER_SIZE = 10
    img = np.ones((640, 480, 3))
    message = BytesIO()
    np.save(message, img)
    message.seek(0)
    b_msg_len, b_message = send_cam_stream.create_message_from_np_array(img, HEADER_SIZE)
    assert b_msg_len == bytes(str(f"{7372928:<{HEADER_SIZE}}"), 'utf-8')
    assert b_message == message.read()

def test_create_socket():
    # FIXME how do we test this
    '''
    Tests that `create_socket` successfully creates a socket 
    '''
    socket = send_cam_stream.create_socket()
    assert True

def test_recv_all():
    # FIXME test won't actually run since we are mocking the recv function
    '''
    Tests that `recv_all` successfully receives a series of Bytes
    and writes it to a BytesIO
    '''
    assert True

def test_canDecodeSuccessfullyNoBBox():
    '''
    Tests that `decode_bboxes_bytes`
    can decode data successfully from a ByteIO
    when there are no bounding boxes
    '''
    message = BytesIO()
    np.save(message, [])
    assert np.array_equal(send_cam_stream.decode_bboxes_bytes(message),
    np.array([]))

def test_canDecodeSuccessfullyManyBBox():
    '''
    Tests that `decode_bboxes_bytes`
    can decode data successfully from a ByteIO
    when there are several bounding boxes
    '''
    message = BytesIO()
    np.save(message, np.ones((3, 6)))
    assert np.array_equal(send_cam_stream.decode_bboxes_bytes(message),
    np.ones((3, 6)))