# CellCraft - Implementation Plan

Here is a concrete implementation plan for developing the Python library known as "CellCraft". The plan is sized for a real first build, not just a conceptual roadmap.

## 1. Initial repository layout

```text
cellcraft/
    __init__.py
    errors.py
    types.py
    pattern.py
    canvas.py
    render.py
    scene.py
    io.py
tests/
    test_pattern_parse.py
    test_pattern_ops.py
    test_canvas.py
    test_renderer.py
    test_scene.py
    test_integration_examples.py
examples/
    example_01_patterns.py
    example_02_canvas_render.py
    example_03_scene_1024x768.py
    example_04_export_sequence.py
tests/golden/
    README.md
pyproject.toml
README.md
```

## 2. Dependency and tooling setup

Use:

- Python 3.12+
- Pillow
- unittest
- ruff
- optionally numpy for test assertions only

Minimal `pyproject.toml` dependencies:

```toml
[project]
name = "cellcraft"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "Pillow>=10.0.0",
]

[project.optional-dependencies]
dev = [
    "ruff>=0.5.0",
    "numpy>=1.26.0",
]

[tool.pytest.ini_options]
testpaths = ["tests"]

[tool.ruff]
line-length = 100
```

## 3. Module responsibilities

### `errors.py`

Define custom exceptions.

```python
class PatternParseError(ValueError): ...
class PatternShapeError(ValueError): ...
class PaletteError(ValueError): ...
class PlacementError(ValueError): ...
class TransformError(ValueError): ...
```

### `types.py`

Define shared types.

```python
from typing import TypeAlias

Symbol: TypeAlias = str | None
RGB: TypeAlias = tuple[int, int, int]
RGBA: TypeAlias = tuple[int, int, int, int]
ColorValue: TypeAlias = RGB | RGBA | None
CellSize: TypeAlias = int | tuple[int, int]
```

### `pattern.py`

Owns `CellPattern` and parsing helpers.

### `canvas.py`

Owns `LogicalCanvas`.

### `render.py`

Owns `PatternRenderer`, palette normalization, PIL rendering helpers.

### `scene.py`

Owns `RasterLayer` and `Scene`.

### `io.py`

Optional export helpers like `save_assets()`.

---

# Phase 1: implement `CellPattern`

## 4. `CellPattern` first-pass API

```python
class CellPattern:
    def __init__(self, data: str | list[list[str | None]]) -> None: ...
    @property
    def width(self) -> int: ...
    @property
    def height(self) -> int: ...
    @property
    def grid(self) -> list[list[str | None]]: ...

    def rot90(self, n: int = 1) -> "CellPattern": ...
    def flip_x(self) -> "CellPattern": ...
    def flip_y(self) -> "CellPattern": ...
    def tile(self, nx: int, ny: int) -> "CellPattern": ...
    def pad(
        self,
        left: int = 0,
        top: int = 0,
        right: int = 0,
        bottom: int = 0,
        value: str | None = ".",
    ) -> "CellPattern": ...
    def replace(self, old: str | None, new: str | None) -> "CellPattern": ...
    def used_symbols(self) -> set[str]: ...
```

## 5. Parsing rules to implement

Support all of these:

```python
CellPattern("AB;BA")
CellPattern("AB\nBA")
CellPattern("""
    AB
    BA
""")
CellPattern([["A", "B"], ["B", "A"]])
```

Normalization steps for string input:

1. replace `;` with `\n`
2. strip leading/trailing blank lines
3. dedent common indentation
4. split into rows
5. remove spaces and tabs inside each row
6. reject empty internal rows
7. ensure rectangularity
8. return `list[list[str]]`

## 6. First test cases for parser

### `tests/test_pattern_parse.py`

Test:

- semicolon rows
- newline rows
- multiline dedent
- ignore spaces/tabs
- rectangular validation
- empty string rejection
- internal blank row rejection
- nested list acceptance

Example:

```python
def test_parse_semicolon_form():
    p = CellPattern("AB;BA")
    assert p.grid == [["A", "B"], ["B", "A"]]
    assert p.width == 2
    assert p.height == 2
```

```python
def test_parse_multiline_dedent():
    p = CellPattern("""
        AB
        BA
    """)
    assert p.grid == [["A", "B"], ["B", "A"]]
```

```python
def test_non_rectangular_pattern_raises():
    with pytest.raises(PatternShapeError):
        CellPattern("AB;B")
```

## 7. First test cases for pattern ops

### `tests/test_pattern_ops.py`

Test:

- `rot90(1)`
- `rot90(2)`
- `rot90(-1)` if supported
- `flip_x`
- `flip_y`
- `tile`
- `pad`
- `replace`
- `used_symbols`

Important: choose and document `rot90` convention once and test against it consistently.

Recommended convention:

- `rot90(1)` = clockwise 90 degrees

---

# Phase 2: implement `LogicalCanvas`

## 8. `LogicalCanvas` first-pass API

```python
class LogicalCanvas:
    def __init__(self, width: int, height: int, fill: str | None = ".") -> None: ...
    @property
    def width(self) -> int: ...
    @property
    def height(self) -> int: ...
    @property
    def grid(self) -> list[list[str | None]]: ...

    def clear(self, fill: str | None = ".") -> None: ...
    def used_symbols(self) -> set[str]: ...
    def place(
        self,
        obj: CellPattern | "LogicalCanvas",
        x: int,
        y: int,
        transparent_symbol: str | None = None,
    ) -> None: ...
```

## 9. Placement behavior

Implement these rules:

- source object may be `CellPattern` or `LogicalCanvas`
- `(x, y)` refers to upper-left source cell on destination
- out-of-bounds placement raises `PlacementError`
- if source cell is `None`, skip write
- if source cell equals `transparent_symbol`, skip write
- all other cells overwrite destination

## 10. Canvas tests

### `tests/test_canvas.py`

Test:

- constructor size/fill
- `clear`
- place pattern at origin
- place pattern at offset
- place canvas onto canvas
- transparent symbol handling
- `None` handling
- out-of-bounds error

Example:

```python
def test_place_pattern():
    canvas = LogicalCanvas(4, 4, fill=".")
    pat = CellPattern("AB;BA")
    canvas.place(pat, x=1, y=1)
    assert canvas.grid == [
        [".", ".", ".", "."],
        [".", "A", "B", "."],
        [".", "B", "A", "."],
        [".", ".", ".", "."],
    ]
```

---

# Phase 3: implement `PatternRenderer`

## 11. `PatternRenderer` first-pass API

```python
class PatternRenderer:
    def __init__(
        self,
        cell_size: int | tuple[int, int],
        palette: dict[str, ColorValue],
        background: ColorValue = None,
    ) -> None: ...

    def render(self, obj: CellPattern | LogicalCanvas) -> Image.Image: ...
```

## 12. Internal renderer helpers

Implement helpers:

- `_normalize_cell_size`
- `_normalize_palette`
- `_validate_palette_for_symbols`
- `_object_dimensions_in_cells`
- `_symbol_to_rgba`

Normalize palette:

- `(r, g, b)` -> `(r, g, b, 255)`
- `(r, g, b, a)` unchanged
- `None` unchanged

## 13. Rendering behavior

For each cell:

- look up symbol in palette
- missing symbol -> `PaletteError`
- `None` -> no draw
- else draw filled rectangle

Render mode should be `RGBA`.

Initial implementation can use `ImageDraw.rectangle`.

## 14. Renderer tests

### `tests/test_renderer.py`

Test:

- square cell size image dimensions
- rectangular cell size image dimensions
- palette normalization
- transparent rendering
- missing palette symbol error
- exact pixel output on tiny examples

Use tiny patterns and assert exact pixels.

Example:

```python
def test_render_2x2_checker_exact_pixels():
    p = CellPattern("AB;BA")
    r = PatternRenderer(
        cell_size=2,
        palette={"A": (0, 0, 0), "B": (255, 255, 255)},
    )
    img = r.render(p)
    assert img.size == (4, 4)
    px = img.load()
    assert px[0, 0] == (0, 0, 0, 255)
    assert px[2, 0] == (255, 255, 255, 255)
    assert px[0, 2] == (255, 255, 255, 255)
```

Strong recommendation: use `numpy.array(img)` in tests where it simplifies assertions.

---

# Phase 4: write spec-backed examples as executable tests

## 15. Example scripts

### `examples/example_01_patterns.py`

Show pattern parsing and transformations.

### `examples/example_02_canvas_render.py`

Show checker tiling and simple canvas rendering.

### `examples/example_03_scene_1024x768.py`

Implement the 1024×768 composite example.

### `examples/example_04_export_sequence.py`

Save a list of generated images.

## 16. Integration tests

### `tests/test_integration_examples.py`

Write tests that execute the same logic as the examples without relying on visual inspection only.

Check:

- image sizes
- expected number of exported files
- expected filenames
- no missing palette symbols
- center and corner assets generated

Example:

```python
def test_scene_1024x768_builds(tmp_path: Path):
    # build final image and exports under tmp_path
    # assert final image size == (1024, 768)
    # assert 9 files exist
```

Examples are how the spec and implementation stay connected.

---

# Phase 5: implement raster composition

## 17. `RasterLayer` first-pass API

```python
@dataclass(slots=True)
class RasterLayer:
    image: Image.Image
    x: float = 0.0
    y: float = 0.0
    rotation_deg: float = 0.0
    scale_x: float = 1.0
    scale_y: float = 1.0
    anchor: str = "top_left"
    opacity: float = 1.0
    resample: str = "nearest"
    z_index: int = 0
```

Validate in `__post_init__`:

- anchor in supported values
- opacity in `[0, 1]`
- resample in supported values
- positive scale values

## 18. `Scene` first-pass API

```python
class Scene:
    def __init__(
        self,
        width: int,
        height: int,
        background: RGBA | None = (0, 0, 0, 0),
    ) -> None: ...

    def add(self, layer: RasterLayer) -> None: ...
    def render(self) -> Image.Image: ...
```

## 19. Transform semantics to lock down

Document and implement exactly this:

- layer image is transformed in its own local space
- scaling and rotation occur about the layer anchor
- `x, y` is the final scene-space location of the anchor
- transformed result is composited into the scene in z-order
- floats are preserved until rasterization
- resample mode controls scaling/rotation sampling

For the first implementation, use PIL’s transform helpers pragmatically rather than building a full affine matrix engine.

## 20. Scene tests

### `tests/test_scene.py`

Test:

- adding one layer
- z-order between layers
- anchor `"top_left"`
- anchor `"center"`
- opacity effect
- nearest resample
- translated placement
- rotated layer produces output image of expected overall size

Do not over-test exact rotated pixels at first; that gets brittle. Favor higher-level behavioral tests.

---

# Phase 6: add export helpers

## 21. `io.py`

Implement something small and boring:

```python
def save_assets(assets: dict[str, Image.Image], out_dir: Path | str) -> None:
    ...
```

Behavior:

- create output directory if needed
- save keys as filenames with `.png` if no suffix
- fail loudly on invalid values

## 22. IO tests

Test:

- directory creation
- filenames
- image saved and reopenable
- wrong object type raises

---

# Concrete week-by-week or milestone plan

## Milestone 1: parsing and pattern transforms

Deliver:

- `CellPattern`
- parser
- `rot90`, `flip_x`, `flip_y`, `tile`, `pad`, `replace`
- tests green

Definition of done:

- all parser and ops tests pass
- examples for pattern creation run

## Milestone 2: logical composition

Deliver:

- `LogicalCanvas`
- `place`
- transparency semantics
- tests green

Definition of done:

- can compose checkerboard into larger symbolic canvas
- out-of-bounds and transparent behavior tested

## Milestone 3: rendering

Deliver:

- `PatternRenderer`
- palette normalization
- RGBA render
- exact pixel tests green

Definition of done:

- can render checkerboards and L-shapes correctly
- tiny pixel tests pass exactly

## Milestone 4: end-to-end static assets

Deliver:

- example scripts
- integration tests
- asset export helper

Definition of done:

- 1024×768 scene can be generated
- 9 image export example works in temp directory

## Milestone 5: scene composition

Deliver:

- `RasterLayer`
- `Scene`
- translation, z-order, anchors
- optional rotation and scaling

Definition of done:

- corner rotations and center assembly work
- scene tests pass
- spec example runs

## Milestone 6: polish

Deliver:

- docstrings
- README quickstart
- better errors
- optional golden image tests

Definition of done:

- library is pleasant to use
- examples mirror spec
- error messages are specific

---

# Suggested first 10 tasks in order

1. Create package skeleton and test scaffolding.
2. Implement parser helpers in `pattern.py`.
3. Implement `CellPattern.__init__`, `width`, `height`, `grid`.
4. Add parser tests and make them pass.
5. Implement `rot90`, `tile`, `replace`, `used_symbols`.
6. Add ops tests and make them pass.
7. Implement `LogicalCanvas`.
8. Add placement tests and make them pass.
9. Implement `PatternRenderer`.
10. Add exact pixel rendering tests.

Only after those 10 should you start `Scene`.

## Next Steps

### Suggested first exact example to code

Before the big 1024×768 example, build this:

```python
checker = CellPattern("AB;BA").tile(2, 2)
canvas = LogicalCanvas(6, 6, fill=".")
canvas.place(checker, 1, 1)

renderer = PatternRenderer(
    cell_size=10,
    palette={
        ".": (128, 128, 128),
        "A": (0, 0, 0),
        "B": (255, 255, 255),
    },
)

img = renderer.render(canvas)
```

If that feels good, the core API is healthy.

---

### Recommended code quality rules

- Make logical objects immutable if practical, or at least return new objects for transforms.
- Keep parsing separate from rendering.
- Do not let `CellPattern` know about palettes.
- Do not let `LogicalCanvas` know about pixels.
- Keep scene transform behavior documented and fixed.
- Prefer explicit errors over silent clipping.

---

### Recommended documentation plan

Write these as you build:

- `README.md`
  - 15-line quickstart
  - one checkerboard example
  - one scene example

- docstrings on all public classes and methods

- `docs/design/0_design_spec.md`
  - the full design spec

- `examples/`
  - runnable scripts that match the README and spec

#### One strong recommendation for testing discipline

Every time you add a new feature, add:

- one unit test
- one usage example

For example, when you add `rot90`, also add a simple example snippet showing `L_shape.rot90(1)`.

That keeps the API from drifting into something only the implementation understands.

---

### Final recommended build order

Build in this order:

1. `CellPattern`
2. `LogicalCanvas`
3. `PatternRenderer`
4. integration example without scene transforms
5. `RasterLayer`
6. `Scene`
7. export helpers
8. polish

That is the lowest-risk path.

---

### Next possible follow-up deliverables

- Task checklist formatted as GitHub issues
- Staged `TODO.md` for the repo
- Initial code skeleton matching this plan
- Pytest starter suite
- CI workflow using GitHub Actions
