# imda-scene-understander-pipeline

Pipeline for IMDA's scene understanding module (to interface with the Robotics Middleware Framework RMF)

## What are we doing?

Basically, building Skynet.

There already exists something called a [Robotics Middleware Framework](),
which is a communication framework that is meant to facilitate communication
between all the different sensors/robots/devices.
If I have it correctly there is a singular system that talks to
all the different robots and devices from different vendors
and can do things like open doors, call lifts, and so on.

The below image from the RMF GitHub repository shows how it's all supposed to
work.

![RMF core infrastructure](https://raw.githubusercontent.com/osrf/rmf_core/master/docs/rmf_core_integration_diagram.png)

This RMF was developed for healthcare ...

What Eric's team is doing is trying to add a "scene understanding manager"
as an extension to the RMF.
To my knowledge, a "scene understanding manager" is something that can take
a scene (videos and signals from cameras/sensors and what not) and understand
_what_ is in that scene.

The scene understanding manager first takes in videos/images from camera feeds.
Then it will look at these images and reconstruct what the actual 3D scene
must look like. Specifically, it draws bounding polygons around the objects in
the scene.

This 3D metadata will then be fed to other RMF modules.
For instance, if its cameras detect a commotion in a
specific area of the mall the RMF dispatcher can reroute patrolling killbots
to terminate the perpetrators (I kid).
There are of course more serious and benign applications like
dynamic route selection or enhanced obstacle avoidance.
For instance, if a robot's cameras detect a medium-term obstruction
(e.g. a pushcart has been moved in the way of its path)
this might be used by the RMF dispatcher to update the trajectories of
any other robots which may have routes passing through that obstruction.

## Why are we doing this?

Not sure. This must be part of a Smart Nation push somewhere or somehow.
I understand from Eric that this is a collaboration of IMDA with many robotics
vendors to improve their technology and everything will be open-sourced.

## What am I doing?

Recall that the first step of the pipeline is to take in the video feeds
and generate an understanding of the scene by annotating the 3D space with
bounding polygons. But as the ML algorithms work on images and not video streams,
I have been asked to write a function in C++
that takes in a video stream (this is a protocol like RTMP, WebRTC, HLS) and returns
a sequence of still images from that video. This will then be fed into the
ML components that do 3D scene reconstruction and object recognition and so on.

I have been asked to use GStreamer (a C framework) to do so.
As I don't have C++ experience and I certainly don't have GStreamer experience,
this is quite a difficult task for me.

## What have I done so far?

16th September:

- read the two documents that Eric sent me,
- understood the medium-picture (augmenting RMF)
- understood the small-picture (scene understanding manager + module)
- understood the tiny picture (my particular task)
- read up about RMF Core [one](https://github.com/osrf/rmf_core/blob/master/docs/faq.md), [two](https://osrf.github.io/ros2multirobotbook/intro.html#robotics-middleware-framework-rmf)
- read up about ROS2 (what RMF builds upon)
- read up about GStreamer
- checked out some promising SO links: [one](https://stackoverflow.com/questions/58878652/how-to-get-video-stream-frame-by-frame-from-gstreamer-pipeline-without-opencv), [two](https://stackoverflow.com/questions/58878652/how-to-get-video-stream-frame-by-frame-from-gstreamer-pipeline-without-opencv), [three](https://stackoverflow.com/questions/59025321/capture-jpeg-images-from-rtsp-gstreamer)
- investigated C++ bindings for GStreamer

Plan for tomorrow (17th September):

- find out how the C++ bindings are going to work
- write the function signature
