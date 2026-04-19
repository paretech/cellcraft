"""LogicalCanvas: mutable cell-space composition surface."""

from __future__ import annotations

from cellcraft.errors import DimensionError, PlacementError
from cellcraft.pattern import CellPattern
from cellcraft.types import OverflowMode, Symbol


class LogicalCanvas:
    """A mutable rectangular grid for composing CellPatterns in cell units."""

    def __init__(self, width: int, height: int, fill: Symbol = ".") -> None:
        if width <= 0 or height <= 0:
            raise DimensionError(f"Canvas dimensions must be positive, got {width}x{height}")
        self._width = width
        self._height = height
        self.fill(fill)

    def __str__(self) -> str:
        return "\n".join(" ".join(c if c is not None else "·" for c in row) for row in self._grid)

    def __repr__(self) -> str:
        flat = [cell for row in self._grid for cell in row]
        if len(set(flat)) == 1:
            fill = flat[0]
            return f"LogicalCanvas({self._width}, {self._height}, fill={fill!r})"
        return f"LogicalCanvas({self._width}, {self._height}, grid={self._grid!r})"

    @property
    def width(self) -> int:
        return self._width

    @property
    def height(self) -> int:
        return self._height

    @property
    def grid(self) -> list[list[Symbol]]:
        return [row[:] for row in self._grid]

    def fill(self, fill: Symbol) -> "LogicalCanvas":
        self._grid = [[fill] * self._width for _ in range(self._height)]
        return self

    @property
    def symbols(self) -> set[str]:
        return {cell for row in self._grid for cell in row if cell is not None}

    def place(
        self,
        obj: CellPattern | "LogicalCanvas",
        x: int,
        y: int,
        transparent_symbol: Symbol = None,
        overflow: OverflowMode = "error",
    ) -> "LogicalCanvas":
        src = obj.grid
        src_h = obj.height
        src_w = obj.width

        if x < 0 or y < 0 or x + src_w > self._width or y + src_h > self._height:
            if overflow == "error":
                raise PlacementError(
                    f"Placement of {src_w}x{src_h} object at ({x}, {y}) "
                    f"is out of bounds for canvas {self._width}x{self._height}"
                )

        for row_i in range(src_h):
            dst_y = y + row_i
            if dst_y < 0 or dst_y >= self._height:
                continue
            for col_i in range(src_w):
                dst_x = x + col_i
                if dst_x < 0 or dst_x >= self._width:
                    continue
                cell = src[row_i][col_i]
                if cell is None:
                    continue
                if transparent_symbol is not None and cell == transparent_symbol:
                    continue
                self._grid[dst_y][dst_x] = cell

        return self
