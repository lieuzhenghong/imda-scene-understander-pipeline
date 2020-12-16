Input: image stream from a Intel Realsense depth camera 
Output: bounding box and depth information of the image,
published on a 
[ROS2 topic](https://index.ros.org/doc/ros2/Tutorials/Topics/Understanding-ROS2-Topics/) 

The output is meant to be consumed by 
RMF Core modules on the central command-and-control server.


## Components of the pipeline

There are four main components in the pipeline:

1. Main I/O dispatcher (Python modules)
2. Object detection ML model (Docker Container)
3. Depth estimator (Python module)
4. Message receiver and broadcaster (EC2 instance)

```

                                 Jetson NX

                  +--------------------------------------+
                  |                                      |
                  |       RGB image    +--------------+  |
                  |    +-------------->+              |  |                  Amazon EC2 instance
                  |    |               |  Docker      |  |
                  |    |               |  Container   |  |                  +-----------------+
                  |    |               |  (ML Model)  |  |                  |                 |
                  |    |               |  (2)         |  |                  |                 |
                  |    |               +-------+------+  |                  |                 |
                  | +--+------------+          |         |                  +-------------+   |
                  | |               |    Bounding boxes  |                  |             |   |
+---------------+ | |               |          |         |                  |             |   |
|               | | |               +<---------+         |  Bounding boxes, | RabbitMQ    |   |
|    Webcam     +---> Main I/O      |                    |   depth data     | receiver    |   |
|               | | | dispatcher    +-------------------------------------->+ and         |   |
+---------------+ | | (1)           |                    |  (over RabbitMQ) | ROS2        |   |
                  | |               +<-----+             |                  | topic       |   |
                  | +-----+---------+      |             |                  | publisher   |   |
                  |       |             Depth            |                  | (4)         |   |
                  |    Bounding         data             |                  +-------------+   |
                  |    boxes               |             |                  |                 |
                  |       |                |             |                  |                 |
                  | +-----v----------------++            |                  |                 |
                  | |                       |            |                  |                 |
                  | |  Depth estimator (3)  |            |                  |                 |
                  | |                       |            |                  +-----------------+
                  | +-----------------------+            |
                  +--------------------------------------+

```

The I/O dispatcher (1) does the vast majority of the work.
It glues together multiple components.
It takes in the webcam stream, 
sends the stream to the ML model (2),
retrieves the bounding boxes from the ML model,
calculates the distance to each object in the scene (3),
then sends the bounding boxes and depth data 
out to the central command-and-control server (4).

The machine learning model (2) 
runs on a Docker container on the Jetson. 
This model is built by the AI scientists.
It takes in an image and returns a list of bounding boxes
around objects the model has detected.

The message receiver and broadcaster (4) 
lives on the command-and-control server.
It is responsible for 
receiving the data from the I/O dispatcher (1)
and publishing the data over a ROS2 topic
to be consumed by RMF Core modules.

I have written a technical deep dive on 
how the I/O dispatcher (1) communicates with 
the ML Docker container (2)
(long story short: Unix sockets).
This is an optional read.