"""CellPattern: symbolic grid motif with transforms and parsing."""

from cellcraft.types import Symbol


class CellPattern:
    """A rectangular symbolic cell grid."""

    def __init__(self, data: str | list[list[Symbol]]) -> None:
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

    def rot90(self, n: int = 1) -> "CellPattern":
        """Return a new pattern rotated clockwise by n * 90 degrees."""
        raise NotImplementedError

    def flip_x(self) -> "CellPattern":
        raise NotImplementedError

    def flip_y(self) -> "CellPattern":
        raise NotImplementedError

    def tile(self, nx: int, ny: int) -> "CellPattern":
        raise NotImplementedError

    def pad(
        self,
        left: int = 0,
        top: int = 0,
        right: int = 0,
        bottom: int = 0,
        value: Symbol = ".",
    ) -> "CellPattern":
        raise NotImplementedError

    def replace(self, old: Symbol, new: Symbol) -> "CellPattern":
        raise NotImplementedError

    def used_symbols(self) -> set[str]:
        raise NotImplementedError
