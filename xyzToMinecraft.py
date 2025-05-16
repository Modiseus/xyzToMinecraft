# @TheWorldFoundry

from amulet.api.selection import SelectionGroup
from amulet.api.level import BaseLevel
from amulet.api.data_types import Dimension

from amulet.api.block import Block  # For working with Blocks
from amulet_nbt import *  # For working with block properties
from amulet.api.errors import ChunkDoesNotExist, ChunkLoadError

import os

class Point:
    def __init__(self, x, y, z, r, g, b):
        self.x = float(x)
        self.y = float(z)
        self.z = -float(y)
        self.r = int(r)
        self.g = int(g)
        self.b = int(b)

    def __repr__(self):
        return f"Point(x={self.x}, y={self.y}, z={self.z}, r={self.r}, g={self.g}, b={self.b})"


def readXYZ():
    points = []
    x_vals, y_vals, z_vals = [], [], []

    with open("XYZ/LIDAR_Punktwolke.xyz", "r") as file:
        for i, line in enumerate(file):
#             if i >= 5:
#                 break

            parts = line.strip().split()
            parts = parts[0:6]
            point = Point(*parts)
            print(point)
            points.append(point)

            x_vals.append(point.x)
            y_vals.append(point.y)
            z_vals.append(point.z)

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
        point.x = point.x - x_range[0] + box.min_x
        point.y = point.y - y_range[0] + box.min_y
        point.z = point.z - z_range[0] + box.min_z


def colorToBlock(r,g,b):
    return Block("minecraft", "stone", {})


def placeBlocksSimple(points, selection: SelectionGroup, world: BaseLevel, dimension: Dimension):

    block_platform = "java"  # the platform the blocks below are defined in
    block_version = (1, 21, 5)  # the version the blocks below are defined in
    block = Block("minecraft", "stone", {})
    block_entity = None

#   alle punkte zu int konvertieren
#   map Position(x,y,z) -> list of rgb
#

    for point in points:
        world.set_version_block(
                            int(point.x),
                            int(point.y),
                            int(point.z),
                            dimension,
                            (block_platform, block_version),
                            block,
                            block_entity,
                        )




def xyz_to_minecraft(
    world: BaseLevel, dimension: Dimension, selection: SelectionGroup, options: dict
):
    print("XYZ to Minecraft starting")

    points, x_range, y_range, z_range = readXYZ()
    box = selection[0]
    toRelativeCoordinates(points, x_range, y_range, z_range, box)

    placeBlocksSimple(points, selection, world, dimension)


    print("XYZ to Minecraft ended")


operation_options = {
#     "Radius": [
#         "int",
#         20,
#     ]
}

export = {
    "name": "XYZ to Minecraft",
    "operation": xyz_to_minecraft,
    "options": operation_options,
}