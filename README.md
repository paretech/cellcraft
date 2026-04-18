# CellCraft

CellCraft is a Python library for building symbolic cell-based patterns and rendering them into images for camera tests, display tests, calibration targets, synthetic artifacts, and engineering visualization.

It is designed around a simple idea:

- define patterns as small symbolic grids
- compose them logically
- render them at any cell size
- assemble final scenes from reusable assets

Examples:

- checkerboards
- corner fiducials
- alignment targets
- masks
- test charts
- animated pattern sequences
- mixed-scale composite scenes

Many imaging test patterns are easier to describe as **cells** than pixels.

---

## Quickstart

```python
import cellcraft as cc

# Define a 2×2 checker motif (several equivalent forms)
checker = cc.CellPattern("AB;BA")
checker = cc.CellPattern("AB\nBA")
checker = cc.CellPattern("""
    AB
    BA
""")

# Tile it into a 4×4 grid
checker_4x4 = checker.tile(2, 2)

# Rotate an L-shape counterclockwise
L = cc.CellPattern("X_;XX")
L_ccw = L.rot90(1)   # counterclockwise 90°

# Other transforms (all return new objects)
checker.flip_x()
checker.flip_y()
checker.pad(left=1, top=1, right=1, bottom=1, value=".")
checker.replace("A", "C")
checker.used_symbols()  # -> {"A", "B"}
```

See [`examples/example_01_patterns.py`](examples/example_01_patterns.py) for a runnable walkthrough of all pattern operations.

---

## Development setup

**Requirements:** Python 3.12+, GNU Make

```sh
make install   # create venv and install package + dev dependencies
make check     # run all quality gates (lint, format-check, typecheck, tests)
```

Common targets:

| Target          | What it does                          |
|-----------------|---------------------------------------|
| `make install`  | Create venv, install editable + dev   |
| `make test`     | Run the test suite                    |
| `make lint`     | Check code style with ruff            |
| `make format-check` | Check formatting (no changes)    |
| `make typecheck`| Static type checking with mypy        |
| `make check`    | All of the above                      |
| `make example`  | Run `examples/example_01_patterns.py` |
| `make clean`    | Remove venv and cache directories     |

Run `make help` to see all targets. The Makefile manages the venv itself — no manual activation needed.
