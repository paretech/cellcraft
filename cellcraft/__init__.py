"""CellCraft: symbolic cell-based pattern generation and raster composition."""

from cellcraft.errors import (
    DimensionError,
    PaletteError,
    PatternParseError,
    PatternShapeError,
    PlacementError,
    TransformError,
)
from cellcraft.pattern import CellPattern
from cellcraft.canvas import LogicalCanvas
from cellcraft.render import PatternRenderer
from cellcraft.scene import RasterLayer, Scene

__all__ = [
    "CellPattern",
    "LogicalCanvas",
    "PatternRenderer",
    "RasterLayer",
    "Scene",
    "DimensionError",
    "PaletteError",
    "PatternParseError",
    "PatternShapeError",
    "PlacementError",
    "TransformError",
]
