#!/usr/bin/env python3

'''
What we have right now:
- bounding boxes in xyxycz (?) format
- depth data per pixel (numpy array)

Step one: do semantic segmentation
Step two: 

object map that maps pixels to object IDs...
(why do I need this?)

Problem now: we have a singular depth value
for a pixel but we don't know what object it belongs to
Solution? 

Aaron suggests to take the median of the already-processed bounding boxes
but I'm not 100% sure that this is correct

I think we do as follows. We first assign each pixel to the set of object IDs.
Then each pixel we choose which object ID to assign it to.

So maybe something like this
Hashmap or array?
'''

import numpy as np
from typing import List, Tuple
from collections import defaultdict

depths = np.random.rand(640, 480)
# depth bb mapping should be a mapping of points to List[id]
# ergo: for each pixel, which object claims it
depth_bb_mapping = {}

BBox = List[float]

obj1 = [2, 2, 10, 10, 1, 2]
obj2 = [0, 0, 5, 3, 2, 2]
obj3 = [11, 11, 13, 12, 1, 2]

bbs: List[BBox] = [obj1, obj2, obj3]

bb_depths = defaultdict(list)

# Idea here is to populate the depth_bb_mapping
for (obj_id, (x1, y1, x2, y2, class_id, something)) in enumerate(bbs):
    for xi in range(x1, x2+1):
        for yi in range(y1, y2+1):
            if (xi, yi) not in depth_bb_mapping:
                depth_bb_mapping[xi, yi] = [obj_id]
                bb_depths[obj_id].append(depths[xi, yi])
            else:
                # we have an overlap
                depth_bb_mapping[xi, yi].append(obj_id)

# Overlaps are the reverse of depth_bb mapping
# For each subset of the objects, it gives the points: List(Point)
# that are claimed by that subset
# Individually separate, collectively exhaustive
# Here's an example
# overlaps = {
#    (0, ) : List[Point] # where a point is a Tuple[int, int]
#    (1, ) : List[Point]
#    (2, )
#    (0, 1)
#    (1, 2):
#    (0, 1, 2 ) ..
#    }
overlaps = defaultdict(list)

# Reverse the map
for key in depth_bb_mapping:
    # What do we do when we have multiple objects overlapping one another
    overlaps[tuple(depth_bb_mapping[key])].append(key)

key_order = sorted(overlaps, key=lambda x: len(x)) # These are all the sorted keys

# Now that we have the overlaps we have to make a decision
# The key assumption is that if we find an overlap, we assign it to the
# one with the highest median
median_depths = defaultdict(int)

Point = Tuple[int, int]

def calculate_median(a: List[Point]) -> float :
    return np.median([depths[x][y] for x, y in a])

def pprint(d: defaultdict(list)) -> None:
    for key in d:
        print(key, len(d[key]))

pprint(overlaps)

# This is to start resolving overlaps
# We first calculate the median depth of each key (ergo no overlap)
# Then for each overlap we assign it to a key with the closest (nearest) median depth 

for key in key_order:
    if len(key) == 1:
        median_depths[key] = (calculate_median(overlaps[key]))
    else:
        # Get the min median object
        max_median = min([((i,), median_depths[(i, )]) for i in key], key=lambda x:x[1])
        print(max_median)
        overlaps[max_median[0]] += overlaps[key]
        overlaps[key] = []


pprint(overlaps)
