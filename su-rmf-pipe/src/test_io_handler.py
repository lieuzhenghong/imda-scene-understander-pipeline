import pyrealsense2 as rs
import send_cam_stream
from unittest.mock import MagicMock, create_autospec
import numpy as np
import pytest

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

@pytest.fixture(autouse=True)
def mock_init(monkeypatch):
    def mock_pipeline(*args, **kwargs):
        return MockRealSensePipeline()

    def mock_config(*args, **kwargs):
        return MockRealSenseConfig()

    monkeypatch.setattr(rs, "pipeline", mock_pipeline)
    monkeypatch.setattr(rs, "config", mock_config)

def test_inite_pipeline():
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

# TODO mock the server, make sure to test different combinations of outputs
def test_send_image_to_server():
    bboxes = send_cam_stream_to_server()

def test_loop():
    loop()
    assert False

def test_main():
    send_cam_stream.main()
    assert True