#!/usr/bin/env python

from typing import List, Tuple
BBox = Tuple[int, int, int, int, float, int]

def send_bboxes_and_depths_to_EC2(bboxes_and_depths:List[Tuple[BBox, float]]) -> None:
    #!/usr/bin/env python
    import pika

    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='52.220.63.39'))
    channel = connection.channel()

    channel.queue_declare(queue='hello')

    # channel.basic_publish(exchange='', routing_key='hello', body='Hello World!')
    channel.basic_publish(exchange='', routing_key='hello', body=bboxes_and_depths)
    print(" [x] Sent 'Hello World!'")
    connection.close()

if __name__ == "__main__":
    from calc_bbox_depths import calculate_bbox_depths
    import numpy as np

    depths = np.random.rand(640, 480)
    obj1 = (2, 2, 639, 479, 1, 2)
    obj2 = (0, 0, 5, 3, 2, 2)
    obj3 = (11, 11, 480, 479, 1, 2)
    bbs: List[BBox] = [obj1, obj2, obj3]

    bbox_and_depths = calculate_bbox_depths(bbs, depths)
    send_bboxes_and_depths_to_EC2(str(bbox_and_depths))
