# Sprint 3 Architecture

Finalising the architecture so we can actually start building it in the next sprint.

We can confirm the architecture thanks to Xin Zheng: 
her hard work confirmed that we can run ROS2 pub/sub in Docker containers
which allows us to have a modular architecture.

## Listener

Each Docker container has a lightweight listener.
The listener's job is to constantly listen for messages 
and MAY return a response AND/OR produce some side effects.

For instance,
the ROS2 module can receive three types of messages:

1. a message of topic name `location_put` with payload `location`.
    Response: none
    Side effects: ROS2 module updates location register.
2. a message of topic name `location_get` with no payload.
    Response: ROS2 module responds with data in location register.
    Side effects: none
3. a message of topic name `objects` with payload `(location, [distance])`.
    Response: none
    Side effects: ROS2 module publishes ROS2 topic.

## Protocol design for the I/O handler and server

Client-server, request-response format.

1. Server (listener) is constantly waiting for a socket connection.
2. Client (or sender) establishes a connection.
3. Once a connection is established, the client sends the message. 
4. Listener decodes the response. 
    Depending on the topic name, it
    *may* perform an action, and 
    *may* send back a response.
    It MUST then close the connection.

This allows freeform communication between client and server.

## Message format

Each message has three parts:
made up of three parts: message size, message topic, and message payload.

The first 10 bytes of the message denote the size in bytes of the entire message.
The next 128 bytes are reserved for topic name (right padded with spaces)
Topic names to a listener must be unique.
Finally all subsequent bytes are the payload: the listener must know how to decode this.

## What happens every frame on the Jetson NX

0. (On demand) ROS2 module container receives location data from robot and updates its own state
1. Every frame the camera pushes out RGB and depth data, received by the I/O dispatcher.
2. I/O dispatcher sends location request topic from ROS2 module container and receives location
3. I/O dispatcher send out RGB image to the ML module container and receives bounding boxes
4. I/O dispatcher calls distance estimator to calculate distance of each detected bounding box 
5. I/O dispatcher sends bundles up location and distance data and sends to ROS2 module container
6. ROS2 module container publishes ROS2 topic

## What happens on the central server

The central server runs ROS2 and subscribes to the published topic.

1. The central server receives the ROS2 topic published by the ROS2 module container
2. It converts the topic to use the global (server's) coordinate system
3. It then publishes that point and object class as a ROS2 topic to be consumed by other ROS2 modules

## Things to worry about

This procedure is blocking which is fine for one ML model
but will be a problem with multiple ML models;
we'll worry about this in the future.

What happens when there is no location saved in the ROS2 module? 
- then we simply discard the bounding box?