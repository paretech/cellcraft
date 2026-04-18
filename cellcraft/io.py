"""Export helpers for saving CellCraft assets to disk."""

from pathlib import Path
from PIL import Image


def save_assets(images: dict[str, Image.Image], output_dir: Path | str) -> None:
    raise NotImplementedError
