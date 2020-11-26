## System architecture overview

Main running on the Jetson host:
takes in webcam stream, sends the webcam images
to the ML model running in a Docker on the Jetson,
gets the depth of each object in the scene,
then sends it out to the central command-and-control server.

## Installation instructions

### Install LibRealSense libraries 

Here I come up with instructions to install LibRealSense and 
get the webcam stream working on the Jetson NX
https://github.com/IntelRealSense/librealsense/issues/7722

And here's my attempt at getting a Dockerfile working:
https://github.com/IntelRealSense/librealsense/issues/7849

### Set up and run ML model Docker container

Build with the command
Run with command 

### Spin up webcam stream client on the Jetson

### (On EC2 instance) Set up RabbitMQ listener

### (On EC2 instance) Publish ROS2 message on custom ROS2 topic
