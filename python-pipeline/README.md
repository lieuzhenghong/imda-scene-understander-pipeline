# README

This README documents the 
architecture of the system I have built,
key objectives and design decisions,
and instructions on how to set up the end-to-end pipe.

## Overview

This is a pipeline that allows the Jetson NX device to send information 
to a central command-and-control server as part of IMDA's VAMA 2 project.

Input: image stream from a Intel Realsense depth camera 
Output: bounding box and depth information of the image,
published on a 
[ROS2 topic](https://index.ros.org/doc/ros2/Tutorials/Topics/Understanding-ROS2-Topics/) 

The output is meant to be consumed by 
RMF Core modules on the central command-and-control server.

## Design goals of the pipeline

- Modular
Well-delineated components
- Extensible

## Components of the pipeline

```

				Jetson NX

                  +--------------------------------------+
                  |                                      |
                  |       RGB image    +--------------+  |
                  |    +-------------->+              |  |                   Amazon EC2 instance
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

There are four main components in the pipeline:

1. Main I/O dispatcher (Python modules)
2. Object detection ML model (Docker Container)
3. Depth estimator (Python module)
4. Message receiver and broadcaster (EC2 instance)

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

## Installation instructions

### Install LibRealSense libraries 

I have written a `install_librealsense.sh` file that
should make the isntallation process very easy.

There are more details available on the IntelRealSense repo:
I come up with instructions to install LibRealSense and 
get the webcam stream working on the Jetson NX 
[here](https://github.com/IntelRealSense/librealsense/issues/7722),
and 
[here's](https://github.com/IntelRealSense/librealsense/issues/7849)
my attempt at getting a Dockerfile working.

### Set up and run ML model Docker container

Build with the command
Run with command 

### Spin up webcam stream client on the Jetson

### (On EC2 instance) Set up RabbitMQ listener

First start running the RabbitMQ Docker on the EC2 instance

Then SSH into the EC2 instance with the command `...`
Ask Jain for the SSH keys

 ```
 pip3 install pika
 ```

First setup the RabbitMQ listener on the 


### (On EC2 instance) Publish ROS2 message on custom ROS2 topic
