"""semvercmp 的既有用例。

覆盖范围有意保持很小：只喂 `1.2.3` 这种简单版本号 —— 三段数值、前导 `v`、
prerelease / build 的字段还原，以及简单版本之间的排序。
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from semvercmp import Version, parse, sorted_versions  # noqa: E402


class ParseTest(unittest.TestCase):

    def test_fields(self):
        version = parse("1.2.3")
        self.assertEqual(version.major, 1)
        self.assertEqual(version.minor, 2)
        self.assertEqual(version.patch, 3)
        self.assertIsInstance(version, Version)

    def test_leading_v(self):
        version = parse("v2.10.0")
        self.assertEqual((version.major, version.minor, version.patch), (2, 10, 0))

    def test_prerelease_tuple(self):
        version = parse("1.2.3-rc.1")
        self.assertEqual(version.prerelease, ("rc", "1"))

    def test_build_retained(self):
        version = parse("1.2.3+build.5")
        self.assertEqual(version.build, "build.5")

    def test_build_absent(self):
        self.assertIsNone(parse("1.2.3").build)

    def test_rejects_missing_segment(self):
        with self.assertRaises(ValueError):
            parse("1.2")

    def test_rejects_invalid_char(self):
        with self.assertRaises(ValueError):
            parse("1.2.x")


class CompareTest(unittest.TestCase):

    def test_patch_order(self):
        self.assertLess(parse("1.2.3"), parse("1.2.4"))

    def test_minor_order(self):
        self.assertLess(parse("1.2.9"), parse("1.3.0"))

    def test_major_order(self):
        self.assertLess(parse("1.9.9"), parse("2.0.0"))

    def test_equal_not_less(self):
        self.assertFalse(parse("1.2.3") < parse("1.2.3"))

    def test_comparison_operators(self):
        self.assertLessEqual(parse("1.2.3"), parse("1.2.3"))
        self.assertGreaterEqual(parse("1.2.3"), parse("1.2.3"))
        self.assertGreater(parse("2.0.0"), parse("1.9.9"))


class SortTest(unittest.TestCase):

    def test_sorted_simple(self):
        versions = [parse("2.0.0"), parse("1.0.0"), parse("1.10.0"), parse("1.2.0")]
        self.assertEqual(
            [version.text() for version in sorted_versions(versions)],
            ["1.0.0", "1.2.0", "1.10.0", "2.0.0"],
        )

    def test_sorted_empty_returns_list(self):
        result = sorted_versions([])
        self.assertIsInstance(result, list)
        self.assertEqual(result, [])


if __name__ == "__main__":
    unittest.main()
