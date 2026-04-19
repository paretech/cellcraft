"""Tests for CellPattern transforms: rot90, flip, tile, pad, replace, used_symbols.

rot90(n) convention: positive n = counterclockwise (matches math / NumPy).
"""

import unittest

from cellcraft.pattern import CellPattern


class TestRot90(unittest.TestCase):
    def setUp(self):
        # AB
        # CD
        self.p = CellPattern("AB;CD")

    def test_rot90_1_ccw(self):
        # CCW 90°: top column goes to right side
        # BD
        # AC
        r = self.p.rot90(1)
        assert r.grid == [["B", "D"], ["A", "C"]]
        assert r.width == 2
        assert r.height == 2

    def test_rot90_2(self):
        # 180° is the same CW or CCW
        # DC
        # BA
        r = self.p.rot90(2)
        assert r.grid == [["D", "C"], ["B", "A"]]

    def test_rot90_3(self):
        # 270° CCW = 90° CW
        # CA
        # DB
        r = self.p.rot90(3)
        assert r.grid == [["C", "A"], ["D", "B"]]

    def test_rot90_4_is_identity(self):
        r = self.p.rot90(4)
        assert r.grid == self.p.grid

    def test_rot90_0_is_identity(self):
        r = self.p.rot90(0)
        assert r.grid == self.p.grid

    def test_rot90_negative_1_is_cw(self):
        # rot90(-1) = 1 step CW = same result as 3 steps CCW
        r = self.p.rot90(-1)
        assert r.grid == self.p.rot90(3).grid

    def test_rot90_negative_explicit_cw(self):
        # AB / CD rotated 1 step CW -> CA / DB
        assert self.p.rot90(-1).grid == [["C", "A"], ["D", "B"]]

    def test_rot90_negative_4_is_identity(self):
        assert self.p.rot90(-4).grid == self.p.grid

    def test_rot90_non_square(self):
        # ABC
        # DEF
        p = CellPattern("ABC;DEF")
        r = p.rot90(1)
        # CCW 90° on 2-row, 3-col -> 3-row, 2-col
        # CF
        # BE
        # AD
        assert r.width == 2
        assert r.height == 3
        assert r.grid == [["C", "F"], ["B", "E"], ["A", "D"]]

    def test_rot90_returns_new_object(self):
        r = self.p.rot90(1)
        assert r is not self.p

    def test_rot90_l_shape_ccw(self):
        # X_
        # XX
        L = CellPattern("X_;XX")
        r = L.rot90(1)
        # CCW 90°:
        # _X
        # XX
        assert r.grid == [["_", "X"], ["X", "X"]]


class TestFlip(unittest.TestCase):
    def setUp(self):
        self.p = CellPattern("AB;CD")

    def test_flip_x(self):
        r = self.p.flip_x()
        assert r.grid == [["B", "A"], ["D", "C"]]

    def test_flip_y(self):
        r = self.p.flip_y()
        assert r.grid == [["C", "D"], ["A", "B"]]

    def test_flip_x_returns_new_object(self):
        r = self.p.flip_x()
        assert r is not self.p

    def test_flip_y_returns_new_object(self):
        r = self.p.flip_y()
        assert r is not self.p

    def test_flip_x_twice_is_identity(self):
        assert self.p.flip_x().flip_x().grid == self.p.grid

    def test_flip_y_twice_is_identity(self):
        assert self.p.flip_y().flip_y().grid == self.p.grid


class TestTile(unittest.TestCase):
    def test_tile_2x2(self):
        p = CellPattern("AB;BA")
        t = p.tile(2, 2)
        assert t.width == 4
        assert t.height == 4
        assert t.grid == [
            ["A", "B", "A", "B"],
            ["B", "A", "B", "A"],
            ["A", "B", "A", "B"],
            ["B", "A", "B", "A"],
        ]

    def test_tile_1x1_is_identity(self):
        p = CellPattern("AB;BA")
        assert p.tile(1, 1).grid == p.grid

    def test_tile_2x1(self):
        p = CellPattern("AB;BA")
        t = p.tile(2, 1)
        assert t.width == 4
        assert t.height == 2

    def test_tile_1x2(self):
        p = CellPattern("AB;BA")
        t = p.tile(1, 2)
        assert t.width == 2
        assert t.height == 4

    def test_tile_returns_new_object(self):
        p = CellPattern("AB;BA")
        assert p.tile(2, 2) is not p


class TestPad(unittest.TestCase):
    def setUp(self):
        self.p = CellPattern("AB;CD")

    def test_pad_all_sides(self):
        r = self.p.pad(left=1, top=1, right=1, bottom=1)
        assert r.width == 4
        assert r.height == 4
        assert r.grid[0] == [".", ".", ".", "."]
        assert r.grid[1] == [".", "A", "B", "."]
        assert r.grid[2] == [".", "C", "D", "."]
        assert r.grid[3] == [".", ".", ".", "."]

    def test_pad_left_only(self):
        r = self.p.pad(left=2)
        assert r.width == 4
        assert r.height == 2
        assert r.grid[0] == [".", ".", "A", "B"]

    def test_pad_custom_value(self):
        r = self.p.pad(top=1, value="X")
        assert r.grid[0] == ["X", "X"]
        assert r.grid[1] == ["A", "B"]

    def test_pad_with_none_value(self):
        r = self.p.pad(left=1, value=None)
        assert r.grid[0][0] is None

    def test_pad_no_args_is_identity(self):
        r = self.p.pad()
        assert r.grid == self.p.grid

    def test_pad_returns_new_object(self):
        assert self.p.pad(left=1) is not self.p


class TestReplace(unittest.TestCase):
    def test_replace_symbol(self):
        p = CellPattern("AB;BA")
        r = p.replace("A", "X")
        assert r.grid == [["X", "B"], ["B", "X"]]

    def test_replace_with_none(self):
        p = CellPattern("AB;BA")
        r = p.replace("A", None)
        assert r.grid == [[None, "B"], ["B", None]]

    def test_replace_none_with_symbol(self):
        p = CellPattern([["A", None], [None, "A"]])
        r = p.replace(None, ".")
        assert r.grid == [["A", "."], [".", "A"]]

    def test_replace_no_match_unchanged(self):
        p = CellPattern("AB;BA")
        r = p.replace("Z", "X")
        assert r.grid == p.grid

    def test_replace_returns_new_object(self):
        p = CellPattern("AB;BA")
        assert p.replace("A", "X") is not p


class TestSymbols(unittest.TestCase):
    def test_basic_symbols(self):
        p = CellPattern("AB;BA")
        assert p.symbols == {"A", "B"}

    def test_excludes_none(self):
        p = CellPattern([["A", None], [None, "B"]])
        assert p.symbols == {"A", "B"}

    def test_single_symbol(self):
        p = CellPattern("AAA;AAA")
        assert p.symbols == {"A"}

    def test_underscore_is_a_symbol(self):
        p = CellPattern("X_;XX")
        assert p.symbols == {"X", "_"}


if __name__ == "__main__":
    unittest.main()
