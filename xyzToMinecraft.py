# @TheWorldFoundry

import numpy as np
from amulet.api.selection import SelectionGroup
from amulet.api.level import BaseLevel
from amulet.api.data_types import Dimension

from amulet.api.block import Block  # For working with Blocks
from amulet_nbt import *  # For working with block properties
from amulet.api.errors import ChunkDoesNotExist, ChunkLoadError

import os


class Point:
    def __init__(self, x, y, z, r, g, b, i, c):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)
        self.r = int(r)
        self.g = int(g)
        self.b = int(b)
        self.i = int(i)
        self.c = int(c)

    def to_minecraft_coordinates(self):
        y = self.y
        self.y = self.z
        self.z = -y

    def __repr__(self):
        return f"Point(x={self.x}, y={self.y}, z={self.z}, r={self.r}, g={self.g}, b={self.b})"

def fill_up_walls(points, box, x_range, y_range, z_range):
    # find any points in the point cloud which has the same x,y coordinates
    points_filled = points.copy()
    
    # THIS WORKED
    # for point in points: 
    #    for y in range(int(box.min_y), int(point.y)):
    #        points_filled.append(Point(point.x, y, point.z, point.r, point.g, point.b, point.i, point.c))

    for x, z in zip(range(int(box.min_x), int(box.min_x + x_range[1] - x_range[0] + 1)), range(int(box.min_z), int(box.min_z + z_range[1] - z_range[0] + 1))):
        matching_xz_points = []
        for point in points:
            if int(point.x) == x and int(point.z) == z:
                matching_xz_points.append(point)
            print("mathing points",  matching_xz_points)
        if len(matching_xz_points) > 0:
            minYValue = np.min([point.y for point in matching_xz_points])
            for y in range(int(box.min_y), int(minYValue)+1):
                points_filled.append(Point(point.x, y, point.z, point.r, point.g, point.b, point.i, point.c))
    """
    for x, z in zip(range(int(box.min_x), int(box.min_x + x_range[1] - x_range[0] + 1)), range(int(box.min_z), int(box.min_z + z_range[1] - z_range[0] + 1))):
        matching_xz_points = []
        for point in points:
            #if int(point.x) == x and int(point.z) == z:
            #    matching_xz_points.append(point)
            #print("mathing points",  matching_xz_points)
        # add points to the point cloud if there are no other points on different z coordinates   
        #unique_y_coord = np.unique([int(point.y) for point in matching_xz_points])
        #print(unique_z_coord, point.z)
        #if np.sum([unique_y_coord > int(point.y)]) == 0:     
            for y in range(int(box.min_y), int(point.y)):
                points_filled.append(Point(point.x, y, point.z, point.r, point.g, point.b, point.i, point.c))
    print(f"Filled up walls number of points: {len(points_filled)} points.")
    """
    return points_filled


def readXYZ():
    points = []
    x_vals, y_vals, z_vals = [], [], []

    with open(
        "C:/Users/diem_/dev/privat/hackdays/2025-05-16_b2abf35e457a_pointcloud/LIDAR_Punktwolke.xyz",
        "r",
    ) as file:
        for i, line in enumerate(file):
            parts = line.strip().split()
            if i > 50000:
                break
            point = Point(*parts)
            point.to_minecraft_coordinates()

            x_vals.append(point.x)
            y_vals.append(point.y)
            z_vals.append(point.z)
            points.append(point)

    # Find ranges
    x_range = (min(x_vals), max(x_vals))
    y_range = (min(y_vals), max(y_vals))
    z_range = (min(z_vals), max(z_vals))

    # Output
    print(f"Loaded {len(points)} points.")
    print(f"x range: {x_range}")
    print(f"y range: {y_range}")
    print(f"z range: {z_range}")

    return points, x_range, y_range, z_range


def toRelativeCoordinates(points, x_range, y_range, z_range, box):
    for point in points:
        point.x = int(point.x - x_range[0] + box.min_x)
        point.y = int(point.y - y_range[0] + box.min_y)
        point.z = int(point.z - z_range[0] + box.min_z)


def placeBlocksSimple(
    points, selection: SelectionGroup, world: BaseLevel, dimension: Dimension
):

    block_platform = "java"  # the platform the blocks below are defined in
    block_version = (1, 21, 5)  # the version the blocks below are defined in
    block_entity = None
    classToBaseName = {
        1: "light_gray_wool",
        2: "gray_wool",
        5: "green_wool",
        6: "granite",
        7: "light_gray_wool",
        8: "light_gray_wool",
        9: "blue_wool",
        17: "black_wool",
    }

    for point in points:
        world.set_version_block(
            int(point.x),
            int(point.y),
            int(point.z),
            dimension,
            (block_platform, block_version),
            Block("minecraft", classToBaseName[point.c], {}),
            block_entity,
        )


def xyz_to_minecraft(
    world: BaseLevel, dimension: Dimension, selection: SelectionGroup, options: dict
):
    print("XYZ to Minecraft starting")

    points, x_range, y_range, z_range = readXYZ()
    box = selection[0]
    toRelativeCoordinates(points, x_range, y_range, z_range, box)

    points = fill_up_walls(points, box,  x_range, y_range, z_range)
    print(f"Loaded after walls filled up: {len(points)} points.")
    placeBlocksSimple(points, selection, world, dimension)

    print("XYZ to Minecraft ended")


operation_options = {}

export = {
    "name": "XYZ to Minecraft",
    "operation": xyz_to_minecraft,
    "options": operation_options,
}
