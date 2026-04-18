"""LogicalCanvas: mutable cell-space composition surface."""

from __future__ import annotations
from cellcraft.pattern import CellPattern
from cellcraft.types import Symbol


class LogicalCanvas:
    """A mutable rectangular grid for composing CellPatterns in cell units."""

    def __init__(self, width: int, height: int, fill: Symbol = ".") -> None:
        raise NotImplementedError

    @property
    def width(self) -> int:
        raise NotImplementedError

    @property
    def height(self) -> int:
        raise NotImplementedError

    @property
    def grid(self) -> list[list[Symbol]]:
        raise NotImplementedError

    def clear(self, fill: Symbol = ".") -> None:
        raise NotImplementedError

    def used_symbols(self) -> set[str]:
        raise NotImplementedError

    def place(
        self,
        obj: CellPattern | "LogicalCanvas",
        x: int,
        y: int,
        transparent_symbol: Symbol = None,
    ) -> None:
        raise NotImplementedError
