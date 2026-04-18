"""LogicalCanvas: mutable cell-space composition surface."""

from __future__ import annotations

from cellcraft.errors import DimensionError, PlacementError
from cellcraft.pattern import CellPattern
from cellcraft.types import Symbol


class LogicalCanvas:
    """A mutable rectangular grid for composing CellPatterns in cell units."""

    def __init__(self, width: int, height: int, fill: Symbol = ".") -> None:
        if width <= 0 or height <= 0:
            raise DimensionError(f"Canvas dimensions must be positive, got {width}x{height}")
        self._width = width
        self._height = height
        self._grid: list[list[Symbol]] = [[fill] * width for _ in range(height)]

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

    def clear(self, fill: Symbol = ".") -> None:
        self._grid = [[fill] * self._width for _ in range(self._height)]

    def used_symbols(self) -> set[str]:
        return {cell for row in self._grid for cell in row if cell is not None}

    def place(
        self,
        obj: CellPattern | "LogicalCanvas",
        x: int,
        y: int,
        transparent_symbol: Symbol = None,
    ) -> "LogicalCanvas":
        src = obj.grid
        src_h = obj.height
        src_w = obj.width

        if x < 0:
            x = self._width + x
        if y < 0:
            y = self._height + y

        if x < 0 or y < 0 or x + src_w > self._width or y + src_h > self._height:
            raise PlacementError(
                f"Placement of {src_w}x{src_h} object at ({x}, {y}) "
                f"is out of bounds for canvas {self._width}x{self._height}"
            )

        for row_i in range(src_h):
            for col_i in range(src_w):
                cell = src[row_i][col_i]
                if cell is None:
                    continue
                if transparent_symbol is not None and cell == transparent_symbol:
                    continue
                self._grid[y + row_i][x + col_i] = cell

        return self
