"""Example 01: Define and inspect basic CellPatterns.

Demonstrates: parsing, rot90, flip_x, flip_y, tile, pad, replace, symbols.
All transforms use the same base pattern (AB;CD) so the effect is easy to follow.
"""

import cellcraft as cc


def show(label: str, pat: cc.CellPattern) -> None:
    print(f"{label}:")
    for line in str(pat).splitlines():
        print("  " + line)


# ---------------------------------------------------------------------------
# Parsing — three equivalent ways to define the same pattern
# ---------------------------------------------------------------------------

p = cc.CellPattern("AB;CD")
show("CellPattern('AB;CD')  — semicolon form", p)

p = cc.CellPattern("AB\nCD")
show("\nCellPattern('AB\\nCD') — newline form", p)

p = cc.CellPattern("""
    AB
    CD
""")
show("\nCellPattern(multiline string)", p)

p = cc.CellPattern([["A", "B"], ["C", "D"]])
show("\nCellPattern([[...]])  — list form", p)

# ---------------------------------------------------------------------------
# Rotations (counterclockwise, matching math / NumPy)
# ---------------------------------------------------------------------------

p = cc.CellPattern("AB;CD")
show("\nbase", p)

for n in (1, 2, 3):
    show(f"rot90({n})   — counterclockwise {n * 90}°", p.rot90(n))

for n in (-1, -2, -3):
    show(f"rot90({n})  — clockwise {abs(n) * 90}°", p.rot90(n))

# ---------------------------------------------------------------------------
# Flips
# ---------------------------------------------------------------------------

show("\nbase", p)
show("flip_x  — horizontal mirror (left ↔ right)", p.flip_x())

show("\nbase", p)
show("flip_y  — vertical mirror (top ↔ bottom)", p.flip_y())

# ---------------------------------------------------------------------------
# Tile
# ---------------------------------------------------------------------------

show("\nbase", p)
t = p.tile(2, 2)
show(f"tile(2, 2)  — {t.width}×{t.height} cells", t)

# ---------------------------------------------------------------------------
# Pad
# ---------------------------------------------------------------------------

show("\nbase", p)
show("pad(left=1, top=1, right=1, bottom=1)", p.pad(left=1, top=1, right=1, bottom=1))

# ---------------------------------------------------------------------------
# Replace
# ---------------------------------------------------------------------------

show("\nbase", p)
show("replace('B', 'X')", p.replace("B", "X"))

# ---------------------------------------------------------------------------
# symbols
# ---------------------------------------------------------------------------

print(f"\nbase.symbols -> {p.symbols}")

# ---------------------------------------------------------------------------
# Method chaining — order matters
#
# pad() extends the current grid with whatever cells already exist at each
# edge, so the same three pads applied in different orders produce very
# different results.
#
# Sequence A: grow left/right first, then top/bottom spans the full width.
# Sequence B: grow top/bottom first, then left/right spans the full height.
# ---------------------------------------------------------------------------

base = cc.CellPattern("AB;AB")

print("\nbase:")
print(base)

a = base.pad(left=4, value="-").pad(right=4, value="+").pad(top=4, bottom=4, value="|")
print("\npad(left=4, '-')  →  pad(right=4, '+')  →  pad(top=4, bottom=4, '|'):")
print(a)

b = base.pad(top=4, bottom=4, value="|").pad(left=4, value="-").pad(right=4, value="+")
print("\npad(top=4, bottom=4, '|')  →  pad(left=4, '-')  →  pad(right=4, '+'):")
print(b)
