# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

The name of this project is "CellCraft".

## Project purpose

This repo implements a Python library for symbolic cell-based pattern generation and raster composition for camera and display test artifacts.

## Source of truth

Full API specification and implementation roadmap are in [docs/design/](docs/design/). An end-to-end scene example is in `docs/design/0_design_spec.md` section 21.2.

- docs/design/0_design_spec.md
- docs/design/1_implementation_plan.md

## Working style

- Follow the implementation plan in milestone order.
- Prefer small, reviewable commits.
- Do not implement future phases unless asked.
- Keep public APIs typed.
- Keep logical domain separate from rendering and scene composition.
- Prefer explicit validation and descriptive exceptions.
- Add or update tests for every behavioral change.
- Do not silently change the spec; propose spec updates separately.
- Every time you add a new feature, add a test, an example and update the readme.
  - For example, when you add `rot90`, also add a simple example snippet showing `L_shape.rot90(1)`. This keeps the API from drifting into something only the implementation understands.

## Code quality

- Python 3.12+
- `python -m unittest` (no pytest). Run tests with: `python -m unittest discover -s tests -v`
- ruff. Run linter with: `ruff check cellcraft/ tests/`
- mypy for type checking
- Assumes the project venv is activated before running these commands.
- Keep modules focused and small.
- Favor immutable return-new-object behavior for transforms where practical.

## When unsure

Ask for the smallest clarification needed or stop with a short note in the commit summary.

## Usage Example

```python
import cellcraft as cc

checker = cc.CellPattern("AB;BA")
canvas = cc.LogicalCanvas(8, 8, fill=".")
renderer = cc.PatternRenderer(
    cell_size=20,
    palette={
        ".": (0,0,0),
        "A": (255,255,255),
        "B": (0,0,0),
    }
)

img = renderer.render(checker.tile(4,4))
```
