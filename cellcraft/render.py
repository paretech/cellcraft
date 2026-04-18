"""PatternRenderer: converts logical objects to PIL images."""

from PIL import Image

from cellcraft.canvas import LogicalCanvas
from cellcraft.pattern import CellPattern
from cellcraft.types import CellSize, ColorValue


class PatternRenderer:
    """Renders a CellPattern or LogicalCanvas to a PIL Image using a symbol palette."""

    def __init__(
        self,
        cell_size: CellSize,
        palette: dict[str, ColorValue],
        background: ColorValue = None,
    ) -> None:
        raise NotImplementedError

    def render(self, obj: CellPattern | LogicalCanvas) -> Image.Image:
        raise NotImplementedError
