#!/usr/bin/env python3

"""
Module to calculate the median distance to each object
given a list of bounding boxes and pixelwise depth data.

Main driver function is calc_bbox_depths, which
takes an input of bounding boxes (List[BBox])
and a 2D array of depths,
and returns a list of bounding boxes with the
median distance to each box:
(List[Tuples[BBox, depth]]).

A BBox is a [x, y, x, y, f, c] tuple
"""

import numpy as np
from typing import List, Tuple, Dict
from collections import defaultdict


# for typing purposes
Point = Tuple[int, int]
BBox = Tuple[int, int, int, int, float, int]


def calculate_median(a: List[Point], depths: np.ndarray) -> float:
    """
    Calculate median depth of a list of points
    """
    return np.median([depths[x][y] for x, y in a])


def pprint(d: defaultdict(list)) -> None:
    """
    Pretty prints a default dict
    """
    for key in d:
        print(key, (d[key]))


def generate_pixel_bb_mapping(bbs: List[BBox]) -> Dict[Point, List[BBox]]:
    """
    Takes a list of bounding boxes and
    returns a mapping of Points to List[BoundingBox];
    for each Point, how many bounding boxes "claim" it?
    In other words, how many bounding boxes does each Point belong to?
    """
    pixel_bb_mapping = {}
    for bounding_box in bbs:
        # Destructuring
        (x1, y1, x2, y2, s, c) = bounding_box
        for xi in range(x1, x2 + 1):
            for yi in range(y1, y2 + 1):
                if (xi, yi) not in pixel_bb_mapping:
                    pixel_bb_mapping[xi, yi] = [bounding_box]
                else:
                    # we have an overlap
                    pixel_bb_mapping[xi, yi].append(bounding_box)

    return pixel_bb_mapping


def generate_bb_pixel_mapping(
    pixel_bb_mapping: Dict[Point, List[BBox]]
) -> Dict[Tuple[BBox], List[Point]]:
    """
    Takes a pixel to bounding box mapping
    and returns a bounding box(es) to pixel mapping:
    In essence it gives the points that are being "claimed"
    by each bounding box.
    For each subset of the set of the bounding boxes,
    we list all the points that belong to that subset.
    Individually separate, collectively exhaustive
    # Here's an example
    # bb_pixel_mapping = {
    #    (0, ) : List[Point] # where a point is a Tuple[int, int]
    #    (1, ) : List[Point]
    #    (2, )
    #    (0, 1)
    #    (1, 2):
    #    (0, 1, 2 ) ..
    """

    mapping = defaultdict(list)

    # Reverse the map
    for key in pixel_bb_mapping:
        mapping[tuple(pixel_bb_mapping[key])].append(key)

    return mapping


def resolve_overlapping_points(
    bb_pixel_mapping: Dict[Tuple[BBox], List[Point]], depths
) -> Dict[Tuple[BBox], List[Point]]:
    """
    Takes a bb_pixel_mapping and returns a "merged" bb_pixel mapping
    """
    # Now that we have the bb_pixel_mapping we have to make a decision
    # The key assumption is that if we find an overlap, we assign it to the
    # one with the highest median
    median_depths = defaultdict(int)
    key_order = sorted(
        bb_pixel_mapping, key=lambda x: len(x)
    )  # These are all the sorted keys
    new_mapping = defaultdict(list)

    for key in key_order:
        if len(key) == 1:
            median_depths[key] = calculate_median(bb_pixel_mapping[key], depths)
            new_mapping[key] = bb_pixel_mapping[key]
        else:
            # Get the min median object
            min_median: Tuple[BBox, float] = min(
                [((i,), median_depths[(i,)]) for i in key], key=lambda x: x[1]
            )
            # Mutate the bb_pixel_mapping: combine them so that each overlapping region is assigned to only one key
            bb_pixel_mapping[min_median[0]] += bb_pixel_mapping[key]

    return new_mapping


def calculate_bbox_depths(
    bbs: List[BBox], depths: np.ndarray
) -> List[Tuple[BBox, float]]:
    """
    Main driver function
    Takes in a list of bounding boxes (tuples of length 6)
    and returns a list of bounding boxes and their (estimated) depths
    """
    pixel_bb_mapping = generate_pixel_bb_mapping(bbs)
    bb_pixel_mapping = generate_bb_pixel_mapping(pixel_bb_mapping)
    deconflicted_bb_pixel_mapping = resolve_overlapping_points(bb_pixel_mapping, depths)

    # We have the "deconflicted" bb pixel mapping which guarantees that
    # each point will be claimed by at most one bounding box
    # To get the result we want we just calculate median depth for each
    # bounding box
    result = [
        (bbox, calculate_median(deconflicted_bb_pixel_mapping[bbox], depths))
        for bbox in deconflicted_bb_pixel_mapping
    ]
    print(result)
    return result


if __name__ == "__main__":
    depths = np.random.rand(640, 480)
    obj1 = (2, 2, 639, 479, 1, 2)
    obj2 = (0, 0, 5, 3, 2, 2)
    obj3 = (11, 11, 480, 479, 1, 2)
    bbs: List[BBox] = [obj1, obj2, obj3]

    calculate_bbox_depths(bbs, depths)
