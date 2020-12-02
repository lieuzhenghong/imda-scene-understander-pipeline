# README

This README documents the 
architecture of the system I have built,
key objectives and design decisions,
and instructions on how to set up the end-to-end pipe.

## Overview

This is a pipeline that allows the Jetson NX device to send information 
to a central command-and-control server as part of IMDA's 
Virtualised Autonomous Mobile Agent (VAMA 2) robotics project.

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

## Design goals of the pipeline

I tried to keep four design goals constantly in mind as I developed
the architecture.

### Simple

The architecture should be as simple as possible
while being able to handle the innate complexity of the domain.
I avoid using libraries that impose a large complexity cost
(e.g. NVIDIA Deepstream, Apache Kafka) unless strictly necessary,
and opt for simpler solutions over solutions that have a higher overhead 
(e.g. Python `sockets` vs. spinning up a HTTP server)

### Top-class documentation

The documentation should be concise yet comprehensive,
and explain not only *what* the components do but also
*why* they were built in a particular way.
It should always be updated to reflect the latest
state of the application,
and should be a pleasure to read.

### Modular

The architecture should be highly modular.
As far as possible, the functionality of the pipeline should be
broken up into separate modules/functions.
It should allow components to be swapped in and out 
without needing significant refactoring.
This is important because our components are constantly being improved
(e.g. the machine learning models by the AI scientists,
or the depth estimation module)
and the architecture needs to support that.

### Extensible

The architecture should allow for new functionality to be added
with minimal fuss.
This is important because the project scope/requirements often change.

## Installation instructions

TODO: work in progress

### Set up the Jetson NX

First, do a `git clone` of this repository
and `cd` to it.

#### Install LibRealSense libraries 

I have written a `install_librealsense.sh` file that
should make the isntallation process very easy.

There are more details available on the IntelRealSense repo:
I come up with instructions to install LibRealSense and 
get the webcam stream working on the Jetson NX 
[here](https://github.com/IntelRealSense/librealsense/issues/7722),
and 
[here's](https://github.com/IntelRealSense/librealsense/issues/7849)
my attempt at getting a Dockerfile working.

#### Set up and run ML model Docker container

TODO

I have prepared a minimal `Dockerfile` available in the Jetson NX.

(**TODO:** put the Dockerfile into the repository)

TODO: streamline this process...

So whichever Dockerfile you use, make sure to do two things:

1. Move `recv_stream_and_send_to_model.py"` into the same folder 
   as the machine learning model function (in this case `B1_detect.py`)
2. Set the `ENTRYPOINT` of the `Dockerfile`
   to `["python3", "-u", "recv_stream_and_send_to_model.py"]`

Build the container with the command `sudo docker build -t testserver .`

Run the container with

``` sh
sudo docker run --rm --network host --runtime nvidia --name ml_server testserver
```

You should see some messages spinning up the ML model
and finally the message `waiting for a connection`:

``` 
Using CUDA device0 _CudaDeviceProperties(name='Xavier', total_memory=7771MB)
...
...
Model Summary: .... 2.00672e+07 gradients
waiting for a connection
```

We are now ready to send the webcam stream to the Docker container.

#### Spin up webcam stream client on the Jetson

Start the webcam stream using `python3 send_cam_stream.py`.

### Set up the EC2 instance

#### Set up RabbitMQ Docker container

TODO

I didn't set this up: Jain did it for me.
Ask Jain how to set up the Docker container to run the RabbitMQ service.

#### Set up RabbitMQ listener

SSH into the EC2 instance with the command 
`ssh ubuntu@52.220.63.39`.
You'll be prompted with the password:
ask Jain for the password. 

Do a `git clone` of this repository and then do `pip3 install pika`
to install the dependencies for the RabbitMQ listener.

Then run the RabbitMQ listener with `python recv_rabbitMQ.py`.
Run this as a background process so it doesn't quit when you exit the SSH server.
You should now see the RabbitMQ listener wait for responses:

```
 [*] Waiting for messages. To exit press CTRL+C
```

### (On EC2 instance) Publish ROS2 message on custom ROS2 topic

TODO, **Not yet implemented**
