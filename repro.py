#!/usr/bin/env python3
"""调用方给的最小复现。

上游报的原话是「排序结果里 1.0.0-rc.2 排到了 1.0.0-rc.10 后面」，
这里把那段排序固定下来；另外顺带核一下带 build 的两个版本是否被判成相等。
修好之后本脚本应当静默退出 0。
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from semvercmp import parse, sorted_versions  # noqa: E402

INPUT = ["1.0.0-rc.10", "1.0.0-rc.2", "1.0.0"]
EXPECTED = ["1.0.0-rc.2", "1.0.0-rc.10", "1.0.0"]


def main():
    broken = []

    got = [version.text() for version in sorted_versions([parse(t) for t in INPUT])]
    print("输入   =", INPUT)
    print("排序后 =", got)
    print("期望   =", EXPECTED)
    if got != EXPECTED:
        broken.append("sort")

    left = parse("1.0.0+build.1")
    right = parse("1.0.0+build.2")
    if not (left == right):
        print("1.0.0+build.1 与 1.0.0+build.2 应判为相等，实际不相等")
        broken.append("equal")

    return 1 if broken else 0


if __name__ == "__main__":
    sys.exit(main())
