# How robot location works

1. Each robot has its own map and coordinate system generated at the start using LIDAR.
3. The robot almost always knows its own position with respect to its own map,
   as it updates its location as it moves.
4. The robot SHOULD be publishing its location as a ROS1 topic.
   - but so far not yet been published yet. (Marcus says this is a trivial task)
   
# How maps are generated

1. There are two different types of map: the simulation map 
    (drawn manually by Marcus on the Traffic Editor)
    and the robots' map
    (generated automatically using LIDAR).
2. When you generate the map with the robot, the map is not perfect. 
   There are LIDAR errors and artifacts.
3. There will always be some differences between RMF core map and the robots' map.
4. In order to get "global" coordinates, we need to reconcile the simulation map
   with the robots' map, and also ensure all robots are using the same map.
   Then we can know that e.g. (x=0.5, y=1.7) is the same point on every map.

## How Marcus is reconciling the maps

- Ideal approach: Floor plan --> LIDAR map to make sure all robots have the same map.
- Current approach: study both maps and find the common scaling and the common points
and make sure they are aligned. If they're not in the same scaling we can transfer
the scaling. To ensure that every point on the LIDAR map is the exact same point 
on the simulation map
- Possible approach: use the simulation map drawn by Marcus in the traffic editor
and export to LIDAR

# Main takeaway

We don't have a way to get "global" coordinates. 
Therefore, our SU Manager will not be able to return the global position
of each obstacle.
Marcus is investigating a way to reconcile the different coordinate systems
(see above).

The map lives in RMF. Which component of RMF? 
Not sure -- Marcus doesn't know yet. He will find out.
