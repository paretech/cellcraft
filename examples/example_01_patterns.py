"""Example 01: Define and inspect basic CellPatterns.

Demonstrates: parsing, rot90, flip_x, flip_y, tile, pad, replace, used_symbols.
"""

import cellcraft as cc

# --- Parsing forms ---

checker = cc.CellPattern("AB;BA")
print("Checker 2x2 (semicolon form):")
for row in checker.grid:
    print(" ".join(str(c) for c in row))

checker_ml = cc.CellPattern("""
    AB
    BA
""")
print("\nChecker 2x2 (multiline dedent):")
for row in checker_ml.grid:
    print(" ".join(str(c) for c in row))

from_list = cc.CellPattern([["A", "B"], ["B", "A"]])
print("\nChecker 2x2 (list form):")
for row in from_list.grid:
    print(" ".join(str(c) for c in row))

# --- Tiling ---

checker_4x4 = checker.tile(2, 2)
print(f"\nChecker tiled 2x2 -> size {checker_4x4.width}x{checker_4x4.height}:")
for row in checker_4x4.grid:
    print(" ".join(str(c) for c in row))

# --- Rotations (clockwise) ---

L = cc.CellPattern("X_;XX")
print("\nL-shape base:")
for row in L.grid:
    print(" ".join(str(c) for c in row))

for n in range(1, 4):
    r = L.rot90(n)
    print(f"\nL.rot90({n}) (clockwise {n*90}°):")
    for row in r.grid:
        print(" ".join(str(c) for c in row))

# --- Flips ---

p = cc.CellPattern("AB;CD")
print("\nflip_x (horizontal mirror):")
for row in p.flip_x().grid:
    print(" ".join(str(c) for c in row))

print("\nflip_y (vertical mirror):")
for row in p.flip_y().grid:
    print(" ".join(str(c) for c in row))

# --- Pad ---

padded = checker.pad(left=1, top=1, right=1, bottom=1, value=".")
print(f"\nChecker padded 1 cell on each side -> size {padded.width}x{padded.height}:")
for row in padded.grid:
    print(" ".join(str(c) for c in row))

# --- Replace ---

replaced = L.replace("_", None)
print("\nL-shape with '_' replaced by None:")
for row in replaced.grid:
    print(" ".join(str(c) if c is not None else "·" for c in row))

# --- used_symbols ---

print(f"\nSymbols in checker: {checker.used_symbols()}")
print(f"Symbols in L-shape: {L.used_symbols()}")
