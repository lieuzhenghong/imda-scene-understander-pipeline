# Should we use RabbitMQ or ROS2 to send messages from the Jetson to the C&C server?

## Introduction

How should we send data over the Internet
from the Jetson NX to the central command-and-control server
(hosted on an EC2 instance)?

We are currently using RabbitMQ to do this, 
but I was tasked by Eric to look into using ROS2 instead.

## Pros of using ROS2 web bridge

### Reduce complexity and dependncy by using only one message broker

ROS2 already has a message broker (over DDS),
and we need to use ROS2 anyway to publish topics to RMF modules,
so it would be ideal if we could simply use ROS2 from end-to-end.
instead of using RabbitMQ from Jetson NX -> EC2
and using ROS2 for inter-EC2 communication.

## Cons of using ROS2 web bridge

https://answers.ros.org/question/292172/is-it-possible-with-ros2-to-send-and-recieve-udp-messages-to-a-certain-ip-address/

> In particular I don't believe there's any commonly used python DDS
> implementation for you to leverage. But we do provide a python implementation
> of the ROS2 API in rclpy that you can import inside your python tool to
> interact with ROS2 directly.

https://answers.ros.org/question/286788/ros2-remote-node-setup/

> In ROS 2, I don't know of a generic solution, but individual DDS
> implementations may have tools for relaying discovery information across the
> internet. Though I don't think that will be very easy to use with ROS 2
> because there isn't a portable way to do it that of which I am aware...
> 
> For both ROS 1 and ROS 2, I wouldn't suggest exposing either publicly to the
> internet for security reasons.
> 
> So in conclusion, I would recommend using VPN for either ROS 1 or ROS 2, for
> both simplicity and security.
 
### 

### No ROS2 Foxy support yet

[This GitHub issue](https://github.com/RobotWebTools/rosbridge_suite/issues/536)
shows that there is still no ROS2 Foxy support even after two months.

### RabbitMQ is lightweight and easy to set up


## Conclusion
