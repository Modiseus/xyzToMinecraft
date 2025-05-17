import numpy as np
from amulet.api.selection import SelectionGroup
from amulet.api.level import BaseLevel
from amulet.api.data_types import Dimension

from amulet.api.block import Block  # For working with Blocks
from amulet_nbt import *  # For working with block properties
from amulet.api.errors import ChunkDoesNotExist, ChunkLoadError

import os


class Point:
    def __init__(self, x, y, z, c):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)
#         self.r = int(r)
#         self.g = int(g)
#         self.b = int(b)
#         self.i = int(i)
        self.c = int(c)

    def to_minecraft_coordinates(self):
        y = self.y
        self.y = self.z
        self.z = -y

    def __repr__(self):
        return f"Point(x={self.x}, y={self.y}, z={self.z}, r={self.r}, g={self.g}, b={self.b})"


def readXYZ():
    points = []
    x_vals, y_vals, z_vals = [], [], []

    with open(
        "XYZ/Bern_West_Ost.xyz",
        "r",
    ) as file:
        for i, line in enumerate(file):
            parts = line.strip().split()
#             if i > 500000:
#                 break
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

def xyz_to_minecraft(
    world: BaseLevel, dimension: Dimension, selection: SelectionGroup, options: dict
):
    print("XYZ to Minecraft starting")

    points, x_range, y_range, z_range = readXYZ()
    box = selection[0]
    toRelativeCoordinates(points, x_range, y_range, z_range, box)

    print(f"Loaded after walls filled up: {len(points)} points.")

    # place Blocks
    block_platform = "java"  # the platform the blocks below are defined in
    block_version = (1, 21, 5)  # the version the blocks below are defined in
    block_entity = None
    classToBaseName = {
        1: "light_gray_wool", # nicht klassifiziert
        2: "gray_wool", # Boden
        3: "green_wool", # Vegetation
        6: "granite", # Gebäude
        9: "water", # Wasser
        17: "black_wool", # Brücken...
    }

    columns = {}

    for point in points:
        if not (point.x, point.z) in columns:
            columns[(point.x, point.z)] = []
        columns[(point.x, point.z)].append(point)


    columnCount = len(columns)
    i = 0
    for (x,z), pointsInColumn in columns.items():
        lowestPoint = pointsInColumn[0]
        for point in pointsInColumn:
            blockType = "light_gray_wool"
            if point.c in classToBaseName:
                blockType = classToBaseName[point.c]

            world.set_version_block(
                        int(point.x),
                        int(point.y),
                        int(point.z),
                        dimension,
                        (block_platform, block_version),
                        Block("minecraft", blockType, {}),
                        block_entity,
                    )
            if point.y < lowestPoint.y:
                lowestPoint = point

        blockType = "light_gray_wool"
        if lowestPoint.c in classToBaseName:
            blockType = classToBaseName[lowestPoint.c]

        # fill column below lowest point
        for y in range(int(box.min_y), int(lowestPoint.y)):
            world.set_version_block(
                                int(lowestPoint.x),
                                int(y),
                                int(lowestPoint.z),
                                dimension,
                                (block_platform, block_version),
                                Block("minecraft", blockType, {}),
                                block_entity,
                            )
        yield i/columnCount
        i+=1


    print("XYZ to Minecraft ended")

operation_options = {}

export = {
    "name": "XYZ to Minecraft",
    "operation": xyz_to_minecraft,
    "options": operation_options,
}
