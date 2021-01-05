#!/usr/bin/env python

from typing import List, Tuple

BBox = Tuple[int, int, int, int, float, int]


def initialise_connection(IPADDR: str):
    """
    Returns a channel
    """
    import pika

    connection = pika.BlockingConnection(pika.ConnectionParameters(host="52.220.63.39"))
    channel = connection.channel()
    return channel


def create_queue(channel, queue_name: str) -> None:
    """
    Creates a queue
    TODO: should queues be durable (ergo survive restarts)?
    Note that `queue_declare` is idempotent so we can re-create existing queues
    with no problem
    """
    channel.queue_declare(queue=queue_name)


def send_bboxes_and_depths_to_EC2(
    channel, bboxes_and_depths: List[Tuple[BBox, float]]
) -> None:
    channel.basic_publish(
        exchange="", routing_key="object_detection", body=bboxes_and_depths
    )
    print(f" [x] Sent {bboxes_and_depths}!")
    connection.close()


if __name__ == "__main__":
    """
    Test harness
    """
    from calc_bbox_depths import calculate_bbox_depths
    import numpy as np

    depths = np.random.rand(640, 480)
    obj1 = (2, 2, 639, 479, 1, 2)
    obj2 = (0, 0, 5, 3, 2, 2)
    obj3 = (11, 11, 480, 479, 1, 2)
    bbs: List[BBox] = [obj1, obj2, obj3]

    bbox_and_depths = calculate_bbox_depths(bbs, depths)
    send_bboxes_and_depths_to_EC2(str(bbox_and_depths))
