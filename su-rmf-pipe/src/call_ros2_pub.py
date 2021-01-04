from listener import Listener
from io import BytesIO


def bdecode(b_full_data: BytesIO) -> (BBox, Location):
    '''
    Unimplemented
    Decode BytesArray into bounding box and location
    XZ to figure out the location format
    '''
    return ([], [])

def pub_ros2(b_full_data: BytesIO):
    '''
    Receive bounding boxes and location data and publish
    as a ROS2 topic
    '''
    b_full_data.seek(0) # Seeks to the start of the file
    # unimplemented: read the data as a file
    bboxes, location = bdecode(b_full_data)
    # Put in ROS2 queue 


def main():
    ros2_listener = Listener(("localhost", 6000), pub_ros2)
    ros2_listener.start_server()