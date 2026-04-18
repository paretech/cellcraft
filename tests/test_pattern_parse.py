"""Tests for CellPattern string and list parsing."""

import unittest

from cellcraft.pattern import CellPattern
from cellcraft.errors import PatternParseError, PatternShapeError


class TestPatternParse(unittest.TestCase):
    def test_parse_semicolon_form(self):
        p = CellPattern("AB;BA")
        assert p.grid == [["A", "B"], ["B", "A"]]
        assert p.width == 2
        assert p.height == 2

    def test_parse_newline_form(self):
        p = CellPattern("AB\nBA")
        assert p.grid == [["A", "B"], ["B", "A"]]

    def test_parse_multiline_dedent(self):
        p = CellPattern("""
            AB
            BA
        """)
        assert p.grid == [["A", "B"], ["B", "A"]]

    def test_parse_multiline_no_leading_indent(self):
        p = CellPattern("""
AB
BA
""")
        assert p.grid == [["A", "B"], ["B", "A"]]

    def test_ignore_spaces_in_rows(self):
        p = CellPattern("A B; B A")
        assert p.grid == [["A", "B"], ["B", "A"]]

    def test_ignore_tabs_in_rows(self):
        p = CellPattern("A\tB;B\tA")
        assert p.grid == [["A", "B"], ["B", "A"]]

    def test_parse_nested_list(self):
        p = CellPattern([["A", "B"], ["B", "A"]])
        assert p.grid == [["A", "B"], ["B", "A"]]
        assert p.width == 2
        assert p.height == 2

    def test_parse_list_with_none(self):
        p = CellPattern([["A", None], [None, "A"]])
        assert p.grid == [["A", None], [None, "A"]]

    def test_empty_string_raises(self):
        with self.assertRaises(PatternParseError):
            CellPattern("")

    def test_blank_only_string_raises(self):
        with self.assertRaises(PatternParseError):
            CellPattern("   \n   ")

    def test_internal_blank_row_raises(self):
        with self.assertRaises(PatternParseError):
            CellPattern("AB\n\nBA")

    def test_non_rectangular_string_raises(self):
        with self.assertRaises(PatternShapeError):
            CellPattern("AB;B")

    def test_non_rectangular_list_raises(self):
        with self.assertRaises(PatternShapeError):
            CellPattern([["A", "B"], ["B"]])

    def test_empty_list_raises(self):
        with self.assertRaises(PatternParseError):
            CellPattern([])

    def test_grid_is_copy(self):
        p = CellPattern("AB;BA")
        g = p.grid
        g[0][0] = "Z"
        assert p.grid[0][0] == "A"

    def test_4x4_pattern(self):
        p = CellPattern("ABCD;DCBA;ABCD;DCBA")
        assert p.width == 4
        assert p.height == 4
        assert p.grid[0] == ["A", "B", "C", "D"]
        assert p.grid[1] == ["D", "C", "B", "A"]

    def test_single_row(self):
        p = CellPattern("ABC")
        assert p.width == 3
        assert p.height == 1
        assert p.grid == [["A", "B", "C"]]

    def test_single_col(self):
        p = CellPattern("A;B;C")
        assert p.width == 1
        assert p.height == 3


class TestPatternStrRepr(unittest.TestCase):
    def test_str_basic(self):
        p = CellPattern("AB;CD")
        assert str(p) == "A B\nC D"

    def test_str_none_renders_as_dot(self):
        p = CellPattern([["A", None], [None, "B"]])
        assert str(p) == "A ·\n· B"

    def test_repr_semicolon_form(self):
        p = CellPattern("AB;CD")
        assert repr(p) == 'CellPattern("AB;CD")'

    def test_repr_roundtrip(self):
        p = CellPattern("AB;CD")
        assert CellPattern("AB;CD").grid == eval(repr(p)).grid

    def test_repr_with_none_falls_back_to_list(self):
        p = CellPattern([["A", None], ["B", "C"]])
        assert repr(p).startswith("CellPattern([")


if __name__ == "__main__":
    unittest.main()
