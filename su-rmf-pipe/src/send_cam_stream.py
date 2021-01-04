'''
This module sends the image to the server

# Remember to set
# export PYTHONPATH=$PYTHONPATH:/usr/local/lib/python3.6/pyrealsense2
# otherwise you will not see pyrealsense2
# you will get ModuleNotFoundError
'''

from io import BytesIO
import numpy as np
from calc_bbox_depths import calculate_bbox_depths
# from send_rabbitmq_bboxes import *
import pyrealsense2 as rs
import socket

from typing import List, Tuple
BBox = Tuple[int, int, int, int, float, int]

def create_socket() -> socket.socket:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    return sock

def create_message_from_np_array(img: np.array, HEADER_SIZE:int = 10) -> (bytes, BytesIO):
    message = BytesIO()
    np.save(message, img)
    msg_len = message.getbuffer().nbytes
    b_msg_len = bytes(str(f"{msg_len:<{HEADER_SIZE}}"), 'utf-8')
    message.seek(0)
    return (b_msg_len, message.read())
    
def recv_all(socket: socket.socket) -> BytesIO:
    '''
    Receives data of msg_len in chunks of 4096 bits
    and returns a BytesIO filled with that data
    '''
    full_data = BytesIO()
    while True:
        data = socket.recv(4096)
        if not data:
            print("All data received!")
            full_data.seek(0)
            break
        full_data.write(data)
    return full_data

def decode_bboxes_bytes(full_data: BytesIO) -> np.array:
    full_data.seek(0)
    assert(full_data.getbuffer().nbytes > 0)
    bboxes = np.load(full_data, allow_pickle=True)
    return bboxes

def send_and_recv_data_from_socket(server_address: Tuple[str, int],
                                   data: any, 
                                   create_message_fn) -> BytesIO:
    HEADER_SIZE = 10
    sock = create_socket()
    sock.connect(server_address)
    try:
        b_msg_len, b_message = create_message_fn(data, HEADER_SIZE)
        sock.sendall(b_msg_len)
        sock.sendall(b_message)
        full_data = recv_all(sock)
    finally:
        print("Closing connection")
        sock.close()
    
    return full_data

def send_image_to_server(img: np.array, server_address: Tuple[str, int]) -> np.array:
    '''
    Sends a colour image to a server at `server_address`.
    The server will detect objects, if any,
    and send back bounding boxes (an Nx6 numpy array)
    '''
    full_data = send_and_recv_data_from_socket(server_address, 
                                               img, 
                                               create_message_from_np_array)
    bboxes = decode_bboxes_bytes(full_data)
    return bboxes

def display_images(depth_image, color_image):
    '''
    Displays image frames that come from the USB camera
    '''
    import cv2
    # Apply colormap on depth image (image must be converted to 8-bit per pixel first)
    depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(
        depth_image, alpha=0.03), cv2.COLORMAP_JET)

    # Stack both images horizontally
    images = np.hstack((color_image, depth_colormap))

    # Show images
    cv2.namedWindow('RealSense', cv2.WINDOW_AUTOSIZE)
    cv2.imshow('RealSense', images)
    cv2.waitKey(1)

def init_pipeline() -> rs.pipeline:
    '''
    Returns a RealSense pipeline
    '''

    # Configure depth and color streams
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
    config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

    # Start streaming
    pipeline.start(config)
    return pipeline

def get_frames(pipeline: rs.pipeline) -> (rs.video_frame, rs.video_frame):
    '''
    Waits for a composite frame in an established pipeline and returns
    the depth and color data
    '''
    # Wait for a coherent pair of frames: depth and color
    frames: rs.composite_frame = pipeline.wait_for_frames()
    depth_frame = frames.get_depth_frame()
    color_frame = frames.get_color_frame()
    return depth_frame, color_frame

def loop(pipeline: rs.pipeline) -> None:
    frame_counter = 0
    # Wait for a coherent pair of frames: depth and color
    depth_frame, color_frame = get_frames(pipeline)
    frame_counter += 1 
    if not depth_frame or not color_frame:
        return

    # Convert images to numpy arrays
    depth_image = np.asanyarray(depth_frame.get_data())
    color_image = np.asanyarray(color_frame.get_data())

    # TODO get the location from ROS1 listener

    # Uncomment this line if you want to see the images
    # display_images(depth_image, color_image)

    print(f"Sending image {frame_counter}...")
    server_address = ('localhost', 6000)
    bboxes = send_image_to_server(color_image, server_address)
    print(f"Images received!")

    # Package to be sent eventually
    package = [bboxes, depth_image]

    # FIXME convert bboxes from numpy arrays to tuples
    # otherwise this function won't work
    # bboxes_and_depths: List[Tuple[BBox, float]] = \
    # calculate_bbox_depths(package)

    # TODO once we have the depths, publish it (and location) to the ROS2 publisher

def main():
    pipeline = init_pipeline()
    try:
        while True:
            loop(pipeline)
    finally:
        # Stop streaming
        pipeline.stop()

if __name__ == "__main__":
    main()