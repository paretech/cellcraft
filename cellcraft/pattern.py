"""CellPattern: symbolic grid motif with transforms and parsing."""

import textwrap

from cellcraft.errors import PatternParseError, PatternShapeError
from cellcraft.types import Symbol


def _parse_string(data: str) -> list[list[Symbol]]:
    data = data.replace(";", "\n")
    lines = data.split("\n")
    # strip leading/trailing blank lines
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    if not lines:
        raise PatternParseError("Pattern string is empty")
    # dedent common indentation
    lines = textwrap.dedent("\n".join(lines)).split("\n")
    rows: list[list[Symbol]] = []
    for line in lines:
        stripped = line.replace(" ", "").replace("\t", "")
        if not stripped:
            raise PatternParseError("Pattern contains an internal blank row")
        rows.append(list(stripped))
    width = len(rows[0])
    for i, row in enumerate(rows):
        if len(row) != width:
            raise PatternShapeError(f"Row {i} has {len(row)} cells but row 0 has {width} cells")
    return rows


def _parse_list(data: list[list[Symbol]]) -> list[list[Symbol]]:
    if not data:
        raise PatternParseError("Pattern list is empty")
    width = len(data[0])
    for i, row in enumerate(data):
        if len(row) != width:
            raise PatternShapeError(f"Row {i} has {len(row)} cells but row 0 has {width} cells")
    return [list(row) for row in data]


def _rotate_ccw(grid: list[list[Symbol]]) -> list[list[Symbol]]:
    rows = len(grid)
    cols = len(grid[0]) if rows > 0 else 0
    return [[grid[j][cols - 1 - i] for j in range(rows)] for i in range(cols)]


def _rotate_cw(grid: list[list[Symbol]]) -> list[list[Symbol]]:
    rows = len(grid)
    cols = len(grid[0]) if rows > 0 else 0
    return [[grid[rows - 1 - j][i] for j in range(rows)] for i in range(cols)]


class CellPattern:
    """A rectangular symbolic cell grid.

    rot90(n) convention: positive n = counterclockwise (matches math / NumPy).
    """

    def __init__(self, data: str | list[list[Symbol]]) -> None:
        if isinstance(data, str):
            self._grid = _parse_string(data)
        elif isinstance(data, list):
            self._grid = _parse_list(data)
        else:
            raise PatternParseError(f"Unsupported input type: {type(data)}")

    def __str__(self) -> str:
        return "\n".join(" ".join(c if c is not None else "·" for c in row) for row in self._grid)

    def __repr__(self) -> str:
        if any(cell is None for row in self._grid for cell in row):
            return f"CellPattern({self._grid!r})"
        return 'CellPattern("' + ";".join("".join(str(c) for c in row) for row in self._grid) + '")'

    @property
    def width(self) -> int:
        return len(self._grid[0]) if self._grid else 0

    @property
    def height(self) -> int:
        return len(self._grid)

    @property
    def grid(self) -> list[list[Symbol]]:
        return [list(row) for row in self._grid]

    def rot90(self, n: int = 1) -> "CellPattern":
        """Rotate by 90-degree steps.

        Positive n: counterclockwise (matches math / NumPy).
        Negative n: clockwise.
        """
        rotate = _rotate_cw if n < 0 else _rotate_ccw
        g = [list(row) for row in self._grid]
        for _ in range(abs(n) % 4):
            g = rotate(g)
        result = object.__new__(CellPattern)
        result._grid = g
        return result

    def flip_x(self) -> "CellPattern":
        """Return a new CellPattern mirrored horizontally (left-right)."""
        result = object.__new__(CellPattern)
        result._grid = [list(reversed(row)) for row in self._grid]
        return result

    def flip_y(self) -> "CellPattern":
        """Return a new CellPattern mirrored vertically (top-bottom)."""
        result = object.__new__(CellPattern)
        result._grid = list(reversed([list(row) for row in self._grid]))
        return result

    def tile(self, nx: int, ny: int) -> "CellPattern":
        """Return a new CellPattern tiled nx times horizontally, ny times vertically."""
        tiled_rows = []
        for _ in range(ny):
            for row in self._grid:
                tiled_rows.append(row * nx)
        result = object.__new__(CellPattern)
        result._grid = tiled_rows
        return result

    def pad(
        self,
        left: int = 0,
        top: int = 0,
        right: int = 0,
        bottom: int = 0,
        value: Symbol = ".",
    ) -> "CellPattern":
        """Return a new CellPattern with padding added on each side."""
        new_width = left + self.width + right
        top_rows = [[value] * new_width for _ in range(top)]
        bottom_rows = [[value] * new_width for _ in range(bottom)]
        middle_rows = [[value] * left + list(row) + [value] * right for row in self._grid]
        result = object.__new__(CellPattern)
        result._grid = top_rows + middle_rows + bottom_rows
        return result

    def replace(self, old: Symbol, new: Symbol) -> "CellPattern":
        """Return a new CellPattern with all occurrences of old replaced by new."""
        result = object.__new__(CellPattern)
        result._grid = [[new if cell == old else cell for cell in row] for row in self._grid]
        return result

    def used_symbols(self) -> set[str]:
        """Return the set of non-None symbols present in the grid."""
        symbols: set[str] = set()
        for row in self._grid:
            for cell in row:
                if cell is not None:
                    symbols.add(cell)
        return symbols
