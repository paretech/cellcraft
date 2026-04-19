"""Tests for LogicalCanvas construction, placement, and transparent symbol handling."""

import unittest

from cellcraft.canvas import LogicalCanvas
from cellcraft.pattern import CellPattern
from cellcraft.errors import DimensionError, PlacementError


class TestLogicalCanvasStrRepr(unittest.TestCase):
    def test_str_uniform(self) -> None:
        canvas = LogicalCanvas(3, 2, fill=".")
        assert str(canvas) == ". . .\n. . ."

    def test_str_mixed(self) -> None:
        canvas = LogicalCanvas(2, 2, fill=".")
        canvas.place(CellPattern("AB;BA"), x=0, y=0)
        assert str(canvas) == "A B\nB A"

    def test_str_none_renders_as_middot(self) -> None:
        canvas = LogicalCanvas(2, 1, fill=None)
        assert str(canvas) == "· ·"

    def test_repr_uniform(self) -> None:
        canvas = LogicalCanvas(3, 2, fill=".")
        assert repr(canvas) == "LogicalCanvas(3, 2, fill='.')"

    def test_repr_uniform_none(self) -> None:
        canvas = LogicalCanvas(2, 2, fill=None)
        assert repr(canvas) == "LogicalCanvas(2, 2, fill=None)"

    def test_repr_mixed_shows_grid(self) -> None:
        canvas = LogicalCanvas(2, 2, fill=".")
        canvas.place(CellPattern("AB;BA"), x=0, y=0)
        assert repr(canvas) == "LogicalCanvas(2, 2, grid=[['A', 'B'], ['B', 'A']])"


class TestLogicalCanvasConstructor(unittest.TestCase):
    def test_size_and_fill(self) -> None:
        canvas = LogicalCanvas(4, 3, fill=".")
        assert canvas.width == 4
        assert canvas.height == 3
        assert canvas.grid == [[".", ".", ".", "."], [".", ".", ".", "."], [".", ".", ".", "."]]

    def test_none_fill(self) -> None:
        canvas = LogicalCanvas(2, 2, fill=None)
        assert canvas.grid == [[None, None], [None, None]]

    def test_invalid_dimensions_raise(self) -> None:
        with self.assertRaises(DimensionError):
            LogicalCanvas(0, 4)
        with self.assertRaises(DimensionError):
            LogicalCanvas(4, 0)

    def test_grid_returns_copy(self) -> None:
        canvas = LogicalCanvas(2, 2, fill=".")
        g = canvas.grid
        g[0][0] = "X"
        assert canvas.grid[0][0] == "."


class TestLogicalCanvasFill(unittest.TestCase):
    def test_fill_resets_grid(self) -> None:
        canvas = LogicalCanvas(2, 2, fill=".")
        canvas._grid[0][0] = "A"
        canvas.fill(".")
        assert canvas.grid == [[".", "."], [".", "."]]

    def test_fill_with_different_symbol(self) -> None:
        canvas = LogicalCanvas(2, 2, fill=".")
        canvas.fill("X")
        assert canvas.grid == [["X", "X"], ["X", "X"]]

    def test_fill_returns_self(self) -> None:
        canvas = LogicalCanvas(2, 2, fill=".")
        assert canvas.fill("X") is canvas


class TestLogicalCanvasSymbols(unittest.TestCase):
    def test_symbols_after_fill(self) -> None:
        canvas = LogicalCanvas(2, 2, fill=".")
        assert canvas.symbols == {"."}

    def test_symbols_excludes_none(self) -> None:
        canvas = LogicalCanvas(2, 2, fill=None)
        assert canvas.symbols == set()

    def test_symbols_after_place(self) -> None:
        canvas = LogicalCanvas(4, 4, fill=".")
        canvas.place(CellPattern("AB;BA"), x=0, y=0)
        assert canvas.symbols == {".", "A", "B"}


class TestLogicalCanvasPlace(unittest.TestCase):
    def test_place_at_origin(self) -> None:
        canvas = LogicalCanvas(2, 2, fill=".")
        canvas.place(CellPattern("AB;BA"), x=0, y=0)
        assert canvas.grid == [["A", "B"], ["B", "A"]]

    def test_place_at_offset(self) -> None:
        canvas = LogicalCanvas(4, 4, fill=".")
        canvas.place(CellPattern("AB;BA"), x=1, y=1)
        assert canvas.grid == [
            [".", ".", ".", "."],
            [".", "A", "B", "."],
            [".", "B", "A", "."],
            [".", ".", ".", "."],
        ]

    def test_place_canvas_onto_canvas(self) -> None:
        src = LogicalCanvas(2, 2, fill="X")
        dst = LogicalCanvas(4, 4, fill=".")
        dst.place(src, x=1, y=1)
        assert dst.grid == [
            [".", ".", ".", "."],
            [".", "X", "X", "."],
            [".", "X", "X", "."],
            [".", ".", ".", "."],
        ]

    def test_place_overwrites_existing(self) -> None:
        canvas = LogicalCanvas(2, 2, fill="A")
        canvas.place(CellPattern("BB;BB"), x=0, y=0)
        assert canvas.grid == [["B", "B"], ["B", "B"]]

    def test_place_multiple_times(self) -> None:
        canvas = LogicalCanvas(3, 1, fill=".")
        canvas.place(CellPattern("A"), x=0, y=0)
        canvas.place(CellPattern("B"), x=2, y=0)
        assert canvas.grid == [["A", ".", "B"]]


class TestLogicalCanvasTransparency(unittest.TestCase):
    def test_none_cell_does_not_overwrite(self) -> None:
        canvas = LogicalCanvas(2, 2, fill=".")
        pat = CellPattern([["A", None], [None, "A"]])
        canvas.place(pat, x=0, y=0)
        assert canvas.grid == [["A", "."], [".", "A"]]

    def test_transparent_symbol_does_not_overwrite(self) -> None:
        canvas = LogicalCanvas(4, 4, fill=".")
        pat = CellPattern("X_;XX")
        canvas.place(pat, x=1, y=1, transparent_symbol="_")
        assert canvas.grid == [
            [".", ".", ".", "."],
            [".", "X", ".", "."],
            [".", "X", "X", "."],
            [".", ".", ".", "."],
        ]

    def test_transparent_symbol_none_means_no_transparency(self) -> None:
        canvas = LogicalCanvas(2, 2, fill=".")
        pat = CellPattern("AB;BA")
        canvas.place(pat, x=0, y=0, transparent_symbol=None)
        assert canvas.grid == [["A", "B"], ["B", "A"]]

    def test_transparent_symbol_overwrites_non_matching(self) -> None:
        canvas = LogicalCanvas(2, 1, fill=".")
        pat = CellPattern("AX")
        canvas.place(pat, x=0, y=0, transparent_symbol="X")
        assert canvas.grid == [["A", "."]]


class TestLogicalCanvasChaining(unittest.TestCase):
    def test_place_returns_self(self) -> None:
        canvas = LogicalCanvas(4, 4, fill=".")
        result = canvas.place(CellPattern("A"), x=0, y=0)
        assert result is canvas

    def test_chain_two_places(self) -> None:
        canvas = (
            LogicalCanvas(4, 4, fill=".")
            .place(CellPattern("A"), x=0, y=0)
            .place(CellPattern("B"), x=3, y=3)
        )
        assert canvas.grid[0][0] == "A"
        assert canvas.grid[3][3] == "B"

    def test_chain_with_negative_index(self) -> None:
        canvas = (
            LogicalCanvas(4, 4, fill=".")
            .place(CellPattern("A"), x=0, y=0)
            .place(CellPattern("B"), x=-1, y=-1)
        )
        assert canvas.grid[0][0] == "A"
        assert canvas.grid[3][3] == "B"


class TestLogicalCanvasBounds(unittest.TestCase):
    def test_out_of_bounds_x_raises(self) -> None:
        canvas = LogicalCanvas(4, 4, fill=".")
        with self.assertRaises(PlacementError):
            canvas.place(CellPattern("AB;BA"), x=3, y=0)

    def test_out_of_bounds_y_raises(self) -> None:
        canvas = LogicalCanvas(4, 4, fill=".")
        with self.assertRaises(PlacementError):
            canvas.place(CellPattern("AB;BA"), x=0, y=3)

    def test_negative_x_wraps(self) -> None:
        canvas = LogicalCanvas(4, 2, fill=".")
        canvas.place(CellPattern("AB"), x=-2, y=0)
        assert canvas.grid == [[".", ".", "A", "B"], [".", ".", ".", "."]]

    def test_negative_y_wraps(self) -> None:
        canvas = LogicalCanvas(2, 4, fill=".")
        canvas.place(CellPattern("A;B"), x=0, y=-2)
        assert canvas.grid == [[".", "."], [".", "."], ["A", "."], ["B", "."]]

    def test_negative_xy_flush_corner(self) -> None:
        canvas = LogicalCanvas(4, 4, fill=".")
        canvas.place(CellPattern("AB;BA"), x=-2, y=-2)
        assert canvas.grid == [
            [".", ".", ".", "."],
            [".", ".", ".", "."],
            [".", ".", "A", "B"],
            [".", ".", "B", "A"],
        ]

    def test_negative_out_of_bounds_raises(self) -> None:
        canvas = LogicalCanvas(4, 4, fill=".")
        with self.assertRaises(PlacementError):
            canvas.place(CellPattern("AB;BA"), x=-100, y=0)

    def test_exact_fit_does_not_raise(self) -> None:
        canvas = LogicalCanvas(2, 2, fill=".")
        canvas.place(CellPattern("AB;BA"), x=0, y=0)
        assert canvas.grid == [["A", "B"], ["B", "A"]]


class TestLogicalCanvasOverflow(unittest.TestCase):
    def test_clip_right_edge(self) -> None:
        canvas = LogicalCanvas(4, 2, fill=".")
        canvas.place(CellPattern("AB;AB"), x=3, y=0, overflow="clip")
        assert canvas.grid == [[".", ".", ".", "A"], [".", ".", ".", "A"]]

    def test_clip_bottom_edge(self) -> None:
        canvas = LogicalCanvas(2, 4, fill=".")
        canvas.place(CellPattern("AB;AB"), x=0, y=3, overflow="clip")
        assert canvas.grid == [[".", "."], [".", "."], [".", "."], ["A", "B"]]

    def test_clip_top_left_corner(self) -> None:
        # Placed at (-1, -1): only src[1][1]="A" lands in bounds at canvas (0, 0).
        canvas = LogicalCanvas(4, 4, fill=".")
        canvas.place(CellPattern("AB;BA"), x=-1, y=-1, overflow="clip")
        assert canvas.grid == [
            ["A", ".", ".", "."],
            [".", ".", ".", "."],
            [".", ".", ".", "."],
            [".", ".", ".", "."],
        ]

    def test_clip_fully_outside_is_noop(self) -> None:
        canvas = LogicalCanvas(4, 4, fill=".")
        canvas.place(CellPattern("AB;BA"), x=10, y=10, overflow="clip")
        assert canvas.grid == [[".", ".", ".", "."] for _ in range(4)]

    def test_clip_respects_transparent_symbol(self) -> None:
        canvas = LogicalCanvas(3, 2, fill=".")
        canvas.place(CellPattern("X_;XX"), x=2, y=0, overflow="clip", transparent_symbol="_")
        assert canvas.grid == [[".", ".", "X"], [".", ".", "X"]]

    def test_error_mode_still_raises(self) -> None:
        canvas = LogicalCanvas(4, 4, fill=".")
        with self.assertRaises(PlacementError):
            canvas.place(CellPattern("AB;BA"), x=3, y=0, overflow="error")

    def test_default_is_error_mode(self) -> None:
        canvas = LogicalCanvas(4, 4, fill=".")
        with self.assertRaises(PlacementError):
            canvas.place(CellPattern("AB;BA"), x=3, y=0)

if __name__ == "__main__":
    unittest.main()
