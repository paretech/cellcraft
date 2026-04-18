"""Example 02: Compose patterns on a LogicalCanvas.

Demonstrates: LogicalCanvas, place(), transparent_symbol, used_symbols.
"""

import cellcraft as cc


def show_canvas(label: str, canvas: cc.LogicalCanvas) -> None:
    print(f"{label}  ({canvas.width}×{canvas.height}):")
    for row in canvas.grid:
        print("  " + "".join(c if c is not None else " " for c in row))


# ---------------------------------------------------------------------------
# Basic placement — checker tiled onto a larger canvas
# ---------------------------------------------------------------------------

checker = cc.CellPattern("AB;BA").tile(2, 2)
canvas = cc.LogicalCanvas(8, 8, fill=".")
canvas.place(checker, x=2, y=2)
show_canvas("checker_4x4 placed at (2, 2)", canvas)

# ---------------------------------------------------------------------------
# Transparent symbol — L-shape with transparent background
# ---------------------------------------------------------------------------

L = cc.CellPattern("X_;XX")

canvas2 = cc.LogicalCanvas(6, 6, fill=".")
canvas2.place(L, x=1, y=1, transparent_symbol="_")
show_canvas("\nL-shape with '_' transparent", canvas2)

# ---------------------------------------------------------------------------
# None cells are always transparent
# ---------------------------------------------------------------------------

pat_with_none = cc.CellPattern([["A", None], [None, "B"]])
canvas3 = cc.LogicalCanvas(4, 4, fill=".")
canvas3.place(pat_with_none, x=1, y=1)
show_canvas("\nPattern with None cells (None is always transparent)", canvas3)

# ---------------------------------------------------------------------------
# Canvas placed onto canvas
# ---------------------------------------------------------------------------

inner = cc.LogicalCanvas(2, 2, fill="Z")
outer = cc.LogicalCanvas(6, 6, fill=".")
outer.place(inner, x=2, y=2)
show_canvas("\nLogicalCanvas placed onto LogicalCanvas", outer)

# ---------------------------------------------------------------------------
# used_symbols
# ---------------------------------------------------------------------------

canvas4 = cc.LogicalCanvas(6, 6, fill=".")
canvas4.place(cc.CellPattern("AB;BA").tile(2, 2), x=1, y=1)
print(f"\nused_symbols: {sorted(canvas4.used_symbols())}")
