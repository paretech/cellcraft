"""Shared type aliases for CellCraft."""

from typing import TypeAlias

Symbol: TypeAlias = str | None
RGB: TypeAlias = tuple[int, int, int]
RGBA: TypeAlias = tuple[int, int, int, int]
ColorValue: TypeAlias = RGB | RGBA | None
CellSize: TypeAlias = int | tuple[int, int]
