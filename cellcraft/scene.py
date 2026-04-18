"""RasterLayer and Scene: pixel-space composition of rendered images."""

from PIL import Image


class RasterLayer:
    """A rendered image with pixel-space placement metadata."""

    def __init__(self, image: Image.Image, x: int = 0, y: int = 0) -> None:
        raise NotImplementedError


class Scene:
    """Composes multiple RasterLayers into a final image."""

    def __init__(self, width: int, height: int, background: tuple[int, int, int, int] = (0, 0, 0, 255)) -> None:
        raise NotImplementedError

    def add(self, layer: RasterLayer) -> None:
        raise NotImplementedError

    def render(self) -> Image.Image:
        raise NotImplementedError
