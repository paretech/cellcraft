# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run all tests
pytest

# Run a single test file
pytest tests/test_pattern_parse.py

# Run a single test
pytest tests/test_pattern_parse.py::test_parse_semicolon_form

# Lint
ruff check .

# Type check
mypy .
```

## Architecture

CellCraft generates symbolic cell-based patterns for camera/display calibration tests. The design separates pattern **definition** (symbolic, cell units) from **rendering** (pixel units).

The package lives in `cell_patterns/` with these modules:

| Module | Responsibility |
|---|---|
| `types.py` | Shared type aliases: `Symbol`, `RGB`, `RGBA`, `ColorValue`, `CellSize` |
| `errors.py` | `PatternParseError`, `PatternShapeError`, `PaletteError`, `PlacementError`, `TransformError` |
| `pattern.py` | `CellPattern` — symbolic grid motif with transforms (`rot90`, `flip_x`, `tile`, `pad`, `replace`) |
| `canvas.py` | `LogicalCanvas` — mutable grid for composing patterns in cell space via `place()` |
| `render.py` | `PatternRenderer` — converts `CellPattern`/`LogicalCanvas` to a PIL `Image` using a symbol→RGBA palette |
| `scene.py` | `RasterLayer` + `Scene` — pixel-space composition of rendered images at arbitrary positions/scales |
| `io.py` | Export helpers (e.g., `save_assets()`) |

**Two composition domains:**
- **Logical domain** (`CellPattern`, `LogicalCanvas`): compose in cell units, preserve symbolic meaning
- **Raster domain** (`PatternRenderer`, `RasterLayer`, `Scene`): render at chosen cell size, compose in pixel space

**Pattern string syntax:** rows separated by `;` or `\n`; multiline strings are dedented automatically; spaces/tabs within rows are stripped; `None` cells are transparent during `place()`.

**Palette:** `dict[str, ColorValue]` mapping symbols to RGB/RGBA tuples. `None` values render as transparent. Missing symbols raise `PaletteError` at render time.

**Placement rule:** `canvas.place(obj, x, y, transparent_symbol=None)` — `None` cells and cells equal to `transparent_symbol` are skipped (not overwritten). Out-of-bounds raises `PlacementError`.

**`rot90` convention:** `rot90(1)` = clockwise 90 degrees.

## Design docs

Full API specification and implementation roadmap are in [docs/design/](docs/design/). The end-to-end calibration scene example (1024×768 with four corner checkerboards and a center cross) is in `docs/design/0_design_spec.md` section 21.2.