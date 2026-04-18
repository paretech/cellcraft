# CellCraft - Design Specification

## 1. Purpose

This library (named "CellCraft") provides a simple, composable API for defining and rendering symbolic cell-based patterns for camera and display test applications.

The library is intended to support:

- Small symbolic motifs such as checkerboards, crosses, bars, masks, and fiducials
- Repeated tiling and simple geometric transforms
- Composition of patterns into larger artifacts
- Rendering with configurable color palettes
- Generation of image sequences
- Final raster composition with independent scaling and subpixel placement

The library is optimized for clarity and control rather than general-purpose vector graphics.

---

## 2. Design goals

### 2.1 Primary goals

The library shall:

- Use a symbolic cell grid as the primary pattern definition model
- Support compact string-based pattern definitions
- Support multiline string pattern definitions as a first-class input format
- Separate logical pattern structure from rendering style
- Support reusable palettes
- Support both logical composition and pixel-space composition
- Remain simple enough for hand-authored engineering patterns

### 2.2 Non-goals

The library is not initially intended to be:

- A full vector drawing package
- A CAD tool
- A real-time graphics engine
- A color-managed ICC workflow system
- A scientific plotting library

---

## 3. Core concepts

The library is divided into two composition domains.

### 3.1 Logical domain

The logical domain operates in cell units.

Objects in this domain:

- `CellPattern`
- `LogicalCanvas`

Use cases:

- Define motifs
- Rotate by 90-degree increments
- Tile motifs
- Combine motifs on cell boundaries
- Preserve symbolic meaning before rasterization

### 3.2 Raster domain

The raster domain operates in pixel units.

Objects in this domain:

- `PatternRenderer`
- `RasterLayer`
- `Scene`

Use cases:

- Render logical artifacts at different cell sizes
- Place rendered artifacts at arbitrary pixel positions
- Compose artifacts with different scales
- Support arbitrary translation, rotation, and scaling

---

## 4. Terminology

### 4.1 Cell

A single symbolic unit in a logical grid.

Examples:

- `'A'`
- `'B'`
- `'.'`
- `'R'`

### 4.2 Symbol

The token stored in a cell. Usually a single-character string.

### 4.3 Palette

A mapping from symbol to RGBA color or transparency.

Example:

```python
palette = {
    'A': None,
    'B': (255, 255, 255),
    '.': (0, 0, 0),
}
```

### 4.4 Pattern

A small symbolic motif, typically reusable.

### 4.5 Canvas

A larger logical grid used to place and combine patterns.

### 4.6 Layer

A rendered raster asset plus transform metadata.

### 4.7 Scene

A collection of raster layers composited into a final image.

---

## 5. Symbol and palette model

### 5.1 Symbol type

The initial implementation shall support symbols as strings.

Preferred usage is single-character strings.

Examples:

- `'A'`
- `'B'`
- `'.'`
- `'0'`
- `'1'`

Multi-character tokens are not required in the initial version.

### 5.2 Palette structure

A palette is a mapping:

```python
dict[str, ColorValue]
```

Where `ColorValue` is one of:

- `None` for transparent
- `(R, G, B)`
- `(R, G, B, A)`

Examples:

```python
palette = {
    'A': None,
    'B': (255, 255, 255),
    'C': (255, 0, 0, 128),
}
```

### 5.3 Palette normalization

The renderer shall normalize all color values internally to RGBA.

Rules:

- `(R, G, B)` becomes `(R, G, B, 255)`
- `(R, G, B, A)` remains unchanged
- `None` remains transparent

### 5.4 Extra palette entries

A palette may contain entries not used by a specific pattern, canvas, or scene. This is explicitly allowed.

This enables:

- Global palettes reused across many artifacts
- Project-level palettes
- Artifact-local overrides
- Future pattern variants without rewriting old palettes

### 5.5 Missing palette entries

Rendering shall fail if a visible symbol is encountered that has no palette entry.

The error should identify the missing symbol.

---

## 6. Pattern definition syntax

### 6.1 Supported input forms

`CellPattern` shall accept at least these forms.

#### String form with newlines

```python
pattern = CellPattern("AB\nBA")
```

#### String form with semicolons

```python
pattern = CellPattern("AB;BA")
```

#### Triple-quoted multiline string

```python
pattern = CellPattern("""
AB
BA
""")
```

#### Nested row form

```python
pattern = CellPattern([
    ['A', 'B'],
    ['B', 'A'],
])
```

### 6.2 Preferred multiline string behavior

For multiline strings, the parser shall:

- Strip leading and trailing blank lines
- Strip common indentation
- Treat each remaining line as one row

So this is valid:

```python
pattern = CellPattern("""
    AB
    BA
""")
```

and should normalize to a 2×2 grid.

### 6.3 Row separators

For string input, both of the following row separators shall be supported:

- Newline
- Semicolon

Initial recommendation: support both, but normalize semicolons to newlines before further parsing.

### 6.4 Whitespace

The initial version should ignore spaces and tabs inside pattern rows.

Example:

```python
CellPattern("A B; B A")
```

shall normalize to:

```python
[
    ['A', 'B'],
    ['B', 'A'],
]
```

If preserving whitespace as a symbol is ever needed, that should be an explicit future feature.

### 6.5 Rectangularity

All patterns shall be rectangular after parsing.

This is invalid:

```text
AB
B
```

and shall raise an error.

---

## 7. Logical domain API

### 7.1 `CellPattern`

Represents a small symbolic motif.

#### Responsibilities

- Store a rectangular symbolic grid
- Expose width and height in cells
- Support local transforms and utility operations

#### Required constructor behavior

```python
CellPattern(data)
```

Where `data` may be:

- Pattern string
- Multiline string
- Nested list of symbols

#### Required properties

- `width: int`
- `height: int`
- `grid: list[list[str | None]]`

#### Required methods

##### `rot90(n=1) -> CellPattern`

Rotate by 90-degree increments. The clockwise or counterclockwise convention shall be documented.

##### `flip_x() -> CellPattern`

Mirror horizontally.

##### `flip_y() -> CellPattern`

Mirror vertically.

##### `tile(nx: int, ny: int) -> CellPattern`

Repeat the pattern in x and y.

##### `pad(left=0, top=0, right=0, bottom=0, value='.') -> CellPattern`

Pad the pattern with a fill symbol.

##### `replace(old, new) -> CellPattern`

Replace one symbol with another.

##### `used_symbols() -> set[str]`

Return the set of symbols present.

#### Optional future methods

- `crop(...)`
- `map_symbols(func)`
- `repeat_x(...)`
- `repeat_y(...)`

### 7.2 `LogicalCanvas`

Represents a larger symbolic composition surface.

#### Responsibilities

- Store a rectangular symbolic grid
- Allow patterns or other logical canvases to be placed on it
- Remain entirely in cell coordinates

#### Constructor

```python
LogicalCanvas(width: int, height: int, fill='.')
```

#### Required properties

- `width: int`
- `height: int`
- `grid: list[list[str | None]]`

#### Required methods

##### `place(obj, x: int, y: int, transparent_symbol=None) -> None`

Place a `CellPattern` or another `LogicalCanvas` at cell coordinates `(x, y)`.

Placement semantics:

- `x`, `y` refer to the upper-left cell of the placed object
- If a source cell equals `transparent_symbol`, it does not overwrite destination
- Initial recommendation: also treat `None` as transparent by default

##### `clear(fill='.') -> None`

Reset canvas to a fill value.

##### `used_symbols() -> set[str]`

Return symbols currently present.

#### Placement bounds policy

Initial recommendation: placement outside bounds shall raise an error unless an explicit clipping mode is added later.

---

## 8. Rendering API

### 8.1 `PatternRenderer`

Converts logical objects to raster images.

#### Responsibilities

- Render a `CellPattern` or `LogicalCanvas` into a PIL image
- Apply cell size and palette
- Optionally apply borders, gaps, or margins later

#### Constructor

```python
PatternRenderer(
    cell_size: int | tuple[int, int],
    palette: dict[str, ColorValue],
    background=None,
)
```

#### Parameters

##### `cell_size`

May be:

- A single integer for square cells
- `(cell_width, cell_height)` for rectangular cells

##### `palette`

Symbol-to-color mapping.

##### `background`

Optional default background fill for the output image. If omitted, transparent background is preferred for RGBA output.

#### Required methods

##### `render(obj: CellPattern | LogicalCanvas) -> PIL.Image.Image`

Render to an RGBA image.

#### Rendering semantics

For each logical cell:

- Lookup symbol in palette
- If result is `None`, do not draw
- Otherwise draw a solid rectangle covering the cell area

#### Pixel geometry

If `cell_size = 20`, then cell `(x, y)` occupies:

- left = `x * 20`
- top = `y * 20`
- right = `(x + 1) * 20`
- bottom = `(y + 1) * 20`

For rectangular cell size `(cw, ch)`, then cell `(x, y)` occupies:

- left = `x * cw`
- top = `y * ch`
- right = `(x + 1) * cw`
- bottom = `(y + 1) * ch`

#### Error behavior

Rendering shall fail if:

- A symbol in the object has no palette mapping
- Cell size is invalid

---

## 9. Raster composition API

### 9.1 `RasterLayer`

Represents a rendered image plus transform metadata.

#### Responsibilities

- Wrap a raster image
- Store transform and composition parameters

#### Constructor

```python
RasterLayer(
    image,
    x=0.0,
    y=0.0,
    rotation_deg=0.0,
    scale_x=1.0,
    scale_y=1.0,
    anchor='top_left',
    opacity=1.0,
    resample='nearest',
    z_index=0,
)
```

#### Parameters

##### `image`

A PIL image, usually from `PatternRenderer.render(...)`.

##### `x`, `y`

Pixel-space position in the final scene.

These may be floats.

##### `rotation_deg`

Rotation in degrees.

##### `scale_x`, `scale_y`

Independent scale factors.

##### `anchor`

Defines how `(x, y)` is interpreted.

Required initial values:

- `'top_left'`
- `'center'`

##### `opacity`

Layer opacity multiplier in range `[0.0, 1.0]`.

##### `resample`

Resampling mode for transforms.

Initial supported values:

- `'nearest'`
- `'bilinear'`

##### `z_index`

Controls render order.

### 9.2 `Scene`

Represents a final raster composition.

#### Responsibilities

- Hold output dimensions
- Manage a set of raster layers
- Composite them into a final image

#### Constructor

```python
Scene(width: int, height: int, background=(0, 0, 0, 0))
```

#### Required methods

##### `add(layer: RasterLayer) -> None`

Add a layer to the scene.

##### `render() -> PIL.Image.Image`

Render all layers in z-order to a final RGBA image.

#### Render order

Initial recommendation: ascending `z_index`, then insertion order.

---

## 10. Coordinate systems

### 10.1 Logical coordinates

Logical coordinates are in cells.

Used by:

- `CellPattern`
- `LogicalCanvas.place(...)`

Convention:

- Origin at upper-left
- +x to the right
- +y downward

### 10.2 Raster coordinates

Raster coordinates are in pixels.

Used by:

- `RasterLayer`
- `Scene`

Convention:

- Origin at upper-left
- +x to the right
- +y downward

---

## 11. Composition rules

### 11.1 Logical composition

Logical composition combines symbols on cell boundaries only.

Valid operations:

- Place pattern on logical canvas
- Place logical canvas on logical canvas
- Tile pattern
- Rotate pattern by 90-degree steps

Logical composition does not support:

- Arbitrary pixel offsets
- Arbitrary-angle rotation
- Fractional scale

### 11.2 Raster composition

Raster composition combines already-rendered images.

Valid operations:

- Arbitrary pixel placement
- Arbitrary-angle rotation
- Independent scaling
- Composition of artifacts rendered with different cell sizes

Raster composition is the correct mechanism for:

- Mixed cell scales
- Non-grid placement
- Subpixel offsets
- Final output layout

---

## 12. Sequence generation

The initial version does not require a dedicated sequence class.

A sequence may simply be represented as:

```python
list[CellPattern]
list[LogicalCanvas]
list[PIL.Image.Image]
list[Scene]
```

A future `PatternSequence` type may be added if timing metadata becomes necessary.

Potential future fields:

- `frames`
- `durations_ms`
- `labels`
- `loop`

---

## 13. Transparency rules

### 13.1 Logical transparency

In logical placement, transparency may be represented by:

- `None`
- An explicitly specified `transparent_symbol`

Recommendation: treat `None` as transparent everywhere in the logical domain.

### 13.2 Raster transparency

In raster rendering and scene composition:

- Images shall be RGBA
- Alpha shall be respected during compositing

---

## 14. Validation requirements

The library shall validate:

- Rectangular pattern shapes
- Nonnegative dimensions
- Valid cell size
- Supported color tuple lengths
- Supported anchors
- Supported resampling modes
- Missing palette entries at render time

---

## 15. Error philosophy

Errors should be explicit and early.

Examples:

- Malformed pattern string
- Non-rectangular rows
- Out-of-bounds logical placement
- Undefined palette symbol
- Unsupported transform option

Errors should name the offending symbol, row, or parameter where possible.

---

## 16. Recommended usage patterns

### 16.1 Define reusable global palette

```python
GLOBAL_PALETTE = {
    '.': (0, 0, 0),
    'A': None,
    'B': (255, 255, 255),
    'R': (255, 0, 0),
    'G': (0, 255, 0),
}
```

This palette may include symbols unused by a particular artifact.

### 16.2 Define pattern as multiline string

```python
checker = CellPattern("""
    AB
    BA
""")
```

### 16.3 Build larger logical artifact

```python
canvas = LogicalCanvas(width=8, height=8, fill='.')
canvas.place(checker.tile(4, 4), x=0, y=0)
```

### 16.4 Render at chosen scale

```python
renderer = PatternRenderer(cell_size=20, palette=GLOBAL_PALETTE)
img = renderer.render(canvas)
```

### 16.5 Composite mixed-scale assets

```python
small = PatternRenderer(cell_size=8, palette=GLOBAL_PALETTE).render(checker)
large = PatternRenderer(cell_size=32, palette=GLOBAL_PALETTE).render(checker)

scene = Scene(width=800, height=600)
scene.add(RasterLayer(small, x=100, y=100))
scene.add(RasterLayer(large, x=250.5, y=180.0, anchor='center'))
final = scene.render()
```

---

## 17. Minimal example implementation target

A first implementation milestone should include:

- `CellPattern`
- `LogicalCanvas`
- `PatternRenderer`
- `RasterLayer`
- `Scene`

and these features:

- String and multiline pattern parsing
- Newline and semicolon row separators
- `rot90`
- `tile`
- Logical placement
- Palette normalization
- RGBA rendering to PIL
- Scene composition with translation
- Optional rotation and scale
- Nearest-neighbor resampling

---

## 18. Future extensions

Not required in the initial version, but anticipated:

- Outlines and gridlines
- Margin and padding at render time
- Clipping modes for logical placement
- Named artifacts and metadata
- Affine transform matrices
- Pattern animation helpers
- Export to GIF, video, or frame sequences
- NumPy array export
- Grayscale and HDR-oriented value modes
- Direct numeric symbol grids
- Symbol classes beyond single characters
- Display gamma and transfer-function helpers

---

## 19. Recommended implementation philosophy

The library should preserve this separation:

- `CellPattern` and `LogicalCanvas` are symbolic
- `PatternRenderer` is styling plus rasterization
- `RasterLayer` and `Scene` are pixel-space composition

That separation is the main reason the API stays clean.

It allows:

- One logical pattern rendered many ways
- One palette reused across many patterns
- One artifact combined with others at independent scale
- Predictable semantics for engineering work

---

## 20. Summary

This design defines a compact symbolic pattern system built around:

- String-authored cell motifs
- Reusable palettes
- Logical grid composition
- Raster rendering
- Scene-based final composition

It is intentionally simple, but it scales well for camera and display test artifacts.

The most important rules are:

- Patterns are symbolic, not pixel-based
- Palettes may be larger than any individual artifact needs
- Multiline string definitions are first-class
- Logical and raster composition are separate concerns

---

## 21. End-to-end example

### 21.1 Composite 1024×768 calibration scene with per-asset exports

This example defines a final scene of size 1024×768 pixels containing:

- Four 4×4 corner grids
- One center cross composed of four non-overlapping 2×2 L-shapes
- Export of the final scene
- Export of each corner grid as its own image
- Export of each center L-shape as its own image

Total output images:

- 1 final composite scene
- 4 corner grid images
- 4 center L-shape images

Total: 9 images

### 21.2 Visual intent

#### Final scene layout

- Top-left corner  
  4×4 checkerboard  
  black and white  
  cell size = 20×20 px

- Top-right corner  
  4×4 checkerboard  
  blue and yellow  
  cell size = 20×40 px  
  rotated +4 degrees

- Bottom-left corner  
  4×4 checkerboard  
  blue and red  
  cell size = 20×40 px  
  rotated -4 degrees

- Bottom-right corner  
  4×4 checkerboard  
  inverted version of top-left  
  white and black  
  cell size = 20×20 px

- Center  
  Four distinct 2×2 L-shapes:
  - base motif = `X_;XX`
  - each rotated by 90 degrees
  - placed so they do not overlap
  - arranged around the center
  - leaving a hole in the middle
  - each shape uses a different color

### 21.3 Pattern definitions

#### 4×4 checkerboard motif

This can be defined by tiling the base 2×2 checker motif.

```python
checker_2x2 = CellPattern("""
AB
BA
""")

checker_4x4 = checker_2x2.tile(2, 2)
```

Equivalent compact form:

```python
checker_2x2 = CellPattern("AB;BA")
checker_4x4 = checker_2x2.tile(2, 2)
```

#### Base 2×2 L-shape motif

```python
L_shape = CellPattern("""
X_
XX
""")
```

Where:

- `X` means filled cell
- `_` means transparent cell

### 21.4 Palettes

A global palette may contain more symbols than are used by any one artifact.

```python
GLOBAL_PALETTE = {
    'A': (0, 0, 0),
    'B': (255, 255, 255),
    'C': (0, 0, 255),
    'D': (255, 255, 0),
    'E': (255, 0, 0),
    'R': (255, 0, 0),
    'G': (0, 255, 0),
    'M': (255, 0, 255),
    'Y': (255, 255, 0),
    '_': None,
}
```

Artifact-specific palettes may be created by selecting or overriding entries from the global palette.

### 21.5 Rendering and layout assumptions

#### Final scene

```python
scene_width = 1024
scene_height = 768
```

#### Corner placement margins

For this example, use a 40 px inset from each image edge.

```python
margin = 40
```

#### Corner grid dimensions

##### Top-left and bottom-right

- 4 columns × 4 rows
- cell size = 20×20 px
- rendered size = 80×80 px

##### Top-right and bottom-left

- 4 columns × 4 rows
- cell size = 20×40 px
- rendered size = 80×160 px before rotation

#### Center L-shapes

Each L-shape:

- 2×2 cells
- rendered with cell size = 24×24 px
- rendered size = 48×48 px

The four rotated L-shapes are placed around the center such that:

- they do not overlap
- their inner corners face inward
- a hole remains at the center

### 21.6 Example code

The following example is written against the proposed API.

```python
from pathlib import Path

# --------------------------------------------------
# Output directory
# --------------------------------------------------

out_dir = Path("exports")
out_dir.mkdir(exist_ok=True)

# --------------------------------------------------
# Patterns
# --------------------------------------------------

checker_2x2 = CellPattern("""
AB
BA
""")

checker_4x4 = checker_2x2.tile(2, 2)

checker_2x2_inverted = CellPattern("""
BA
AB
""")

checker_4x4_inverted = checker_2x2_inverted.tile(2, 2)

L_shape = CellPattern("""
X_
XX
""")

# --------------------------------------------------
# Palettes
# --------------------------------------------------

palette_bw = {
    'A': (0, 0, 0),
    'B': (255, 255, 255),
}

palette_by = {
    'A': (0, 0, 255),
    'B': (255, 255, 0),
}

palette_br = {
    'A': (0, 0, 255),
    'B': (255, 0, 0),
}

palette_cross_red = {
    'X': (255, 0, 0),
    '_': None,
}

palette_cross_green = {
    'X': (0, 255, 0),
    '_': None,
}

palette_cross_magenta = {
    'X': (255, 0, 255),
    '_': None,
}

palette_cross_yellow = {
    'X': (255, 255, 0),
    '_': None,
}

# --------------------------------------------------
# Renderers
# --------------------------------------------------

renderer_bw_square = PatternRenderer(
    cell_size=(20, 20),
    palette=palette_bw,
)

renderer_by_rect = PatternRenderer(
    cell_size=(20, 40),
    palette=palette_by,
)

renderer_br_rect = PatternRenderer(
    cell_size=(20, 40),
    palette=palette_br,
)

renderer_cross_red = PatternRenderer(
    cell_size=(24, 24),
    palette=palette_cross_red,
)

renderer_cross_green = PatternRenderer(
    cell_size=(24, 24),
    palette=palette_cross_green,
)

renderer_cross_magenta = PatternRenderer(
    cell_size=(24, 24),
    palette=palette_cross_magenta,
)

renderer_cross_yellow = PatternRenderer(
    cell_size=(24, 24),
    palette=palette_cross_yellow,
)

# --------------------------------------------------
# Render corner assets
# --------------------------------------------------

img_corner_tl = renderer_bw_square.render(checker_4x4)
img_corner_tr = renderer_by_rect.render(checker_4x4)
img_corner_bl = renderer_br_rect.render(checker_4x4)
img_corner_br = renderer_bw_square.render(checker_4x4_inverted)

# Save corner exports
img_corner_tl.save(out_dir / "corner_top_left.png")
img_corner_tr.save(out_dir / "corner_top_right.png")
img_corner_bl.save(out_dir / "corner_bottom_left.png")
img_corner_br.save(out_dir / "corner_bottom_right.png")

# --------------------------------------------------
# Render center L-shape assets
# --------------------------------------------------

img_L_0 = renderer_cross_red.render(L_shape.rot90(0))
img_L_1 = renderer_cross_green.render(L_shape.rot90(1))
img_L_2 = renderer_cross_magenta.render(L_shape.rot90(2))
img_L_3 = renderer_cross_yellow.render(L_shape.rot90(3))

# Save L-shape exports
img_L_0.save(out_dir / "cross_L_0.png")
img_L_1.save(out_dir / "cross_L_1.png")
img_L_2.save(out_dir / "cross_L_2.png")
img_L_3.save(out_dir / "cross_L_3.png")

# --------------------------------------------------
# Build final scene
# --------------------------------------------------

scene = Scene(width=1024, height=768, background=(32, 32, 32, 255))

# Corner placement margins
margin = 40

# Corner dimensions
w_sq, h_sq = img_corner_tl.size
w_rect, h_rect = img_corner_tr.size

# Top-left
scene.add(RasterLayer(
    image=img_corner_tl,
    x=margin,
    y=margin,
    anchor="top_left",
    z_index=0,
))

# Top-right
scene.add(RasterLayer(
    image=img_corner_tr,
    x=1024 - margin - w_rect / 2,
    y=margin + h_rect / 2,
    rotation_deg=4,
    anchor="center",
    resample="nearest",
    z_index=0,
))

# Bottom-left
scene.add(RasterLayer(
    image=img_corner_bl,
    x=margin + w_rect / 2,
    y=768 - margin - h_rect / 2,
    rotation_deg=-4,
    anchor="center",
    resample="nearest",
    z_index=0,
))

# Bottom-right
scene.add(RasterLayer(
    image=img_corner_br,
    x=1024 - margin - w_sq,
    y=768 - margin - h_sq,
    anchor="top_left",
    z_index=0,
))

# --------------------------------------------------
# Center cross layout
# --------------------------------------------------

wL, hL = img_L_0.size

cx = 1024 / 2
cy = 768 / 2

gap = 8

scene.add(RasterLayer(
    image=img_L_0,
    x=cx - gap / 2 - wL,
    y=cy - gap / 2 - hL,
    anchor="top_left",
    z_index=1,
))

scene.add(RasterLayer(
    image=img_L_1,
    x=cx + gap / 2,
    y=cy - gap / 2 - hL,
    anchor="top_left",
    z_index=1,
))

scene.add(RasterLayer(
    image=img_L_2,
    x=cx + gap / 2,
    y=cy + gap / 2,
    anchor="top_left",
    z_index=1,
))

scene.add(RasterLayer(
    image=img_L_3,
    x=cx - gap / 2 - wL,
    y=cy + gap / 2,
    anchor="top_left",
    z_index=1,
))

# --------------------------------------------------
# Render and save final scene
# --------------------------------------------------

final_img = scene.render()
final_img.save(out_dir / "scene_1024x768.png")
```

### 21.7 Expected exported files

This example produces these files:

```text
exports/
    scene_1024x768.png
    corner_top_left.png
    corner_top_right.png
    corner_bottom_left.png
    corner_bottom_right.png
    cross_L_0.png
    cross_L_1.png
    cross_L_2.png
    cross_L_3.png
```

Total: 9 images.

### 21.8 Notes on geometry

#### Top-left and bottom-right checkerboards

These use square 20×20 cells.

Rendered grid size:

```python
4 * 20 == 80
```

in both width and height.

#### Top-right and bottom-left checkerboards

These use rectangular 20×40 cells.

Rendered grid size:

```python
width = 4 * 20   # 80 px
height = 4 * 40  # 160 px
```

These are then rotated in raster space, not logical space.

#### Center cross

The four L-shapes are not logically combined into one single symbolic canvas in this example. Instead, each is:

- Rendered independently
- Colorized independently
- Positioned independently in the scene

This is the preferred approach when:

- Each component has its own color
- Components may be exported independently
- Final composition is pixel-space oriented

### 21.9 Why this example matters

This example demonstrates the intended division of responsibilities.

#### `CellPattern`

Used to define:

- Checker motif
- Inverted checker motif
- L-shape motif

#### `PatternRenderer`

Used to create:

- Square black and white assets
- Rectangular blue and yellow assets
- Rectangular blue and red assets
- Colorized L-shape assets

#### `RasterLayer`

Used to:

- Position assets in corners
- Rotate selected grids
- Assemble center geometry

#### `Scene`

Used to:

- Define final output dimensions
- Compose all raster assets into the final image

### 21.10 Optional future refinement

A future convenience helper may be added for exporting a batch of assets:

```python
export_assets({
    "scene_1024x768": final_img,
    "corner_top_left": img_corner_tl,
    "corner_top_right": img_corner_tr,
    "corner_bottom_left": img_corner_bl,
    "corner_bottom_right": img_corner_br,
    "cross_L_0": img_L_0,
    "cross_L_1": img_L_1,
    "cross_L_2": img_L_2,
    "cross_L_3": img_L_3,
}, out_dir="exports")
```

This is not required for the initial design.

### 21.11 Design takeaway

This example shows why the API is split into:

- Logical symbolic definition
- Rendering
- Raster composition

If these were collapsed into one object, it would be much harder to support:

- Different cell sizes
- Different palettes
- Rotated corner assets
- Independent export of subcomponents
- Final arbitrary scene composition

