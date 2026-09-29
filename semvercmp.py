"""semvercmp：语义化版本（SemVer）的解析、比较与排序。

对外入口::

    from semvercmp import Version, parse, compare, sorted_versions

只用标准库。
"""

import re

__all__ = ["Version", "parse", "compare", "sorted_versions"]

#: 版本号整体形状：MAJOR.MINOR.PATCH[-prerelease][+build]，前导 v 可选。
_SPEC = re.compile(
    r"^v?(\d+)\.(\d+)\.(\d+)(?:-([0-9A-Za-z.-]+))?(?:\+([0-9A-Za-z.-]+))?$"
)

#: 单个标识符允许的字符。
_IDENT = re.compile(r"^[0-9A-Za-z-]+$")


class Version(object):
    """一个已经解析好的语义化版本号。

    字段：``major`` / ``minor`` / ``patch`` / ``prerelease``（字符串元组）/ ``build``（字符串或 None）。
    """

    def __init__(self, major, minor, patch, prerelease=(), build=None):
        self.major = int(major)
        self.minor = int(minor)
        self.patch = int(patch)
        self.prerelease = tuple(prerelease)
        self.build = build

    # -- 文本 ---------------------------------------------------------------

    def text(self):
        """还原成版本字符串。"""
        out = "%d.%d.%d" % (self.major, self.minor, self.patch)
        if self.prerelease:
            out += "-" + ".".join(self.prerelease)
        if self.build is not None:
            out += "+" + self.build
        return out

    def __str__(self):
        return self.text()

    def __repr__(self):
        return "Version(%r)" % (self.text(),)

    # -- 比较 ---------------------------------------------------------------

    def compare(self, other):
        """与另一个 ``Version`` 比大小：``-1`` / ``0`` / ``1``。"""
        if not isinstance(other, Version):
            return NotImplemented

        mine = (self.major, self.minor, self.patch)
        theirs = (other.major, other.minor, other.patch)
        if mine != theirs:
            return -1 if mine < theirs else 1

        if self.prerelease and not other.prerelease:
            return 1
        if other.prerelease and not self.prerelease:
            return -1

        if self.prerelease and other.prerelease:
            left = ".".join(self.prerelease)
            right = ".".join(other.prerelease)
            if left != right:
                return -1 if left < right else 1

        left_build = self.build or ""
        right_build = other.build or ""
        if left_build != right_build:
            return -1 if left_build < right_build else 1

        return 0

    def __lt__(self, other):
        result = self.compare(other)
        if result is NotImplemented:
            return NotImplemented
        return result < 0

    def __le__(self, other):
        result = self.compare(other)
        if result is NotImplemented:
            return NotImplemented
        return result <= 0

    def __gt__(self, other):
        result = self.compare(other)
        if result is NotImplemented:
            return NotImplemented
        return result > 0

    def __ge__(self, other):
        result = self.compare(other)
        if result is NotImplemented:
            return NotImplemented
        return result >= 0

    def __hash__(self):
        return hash(
            (self.major, self.minor, self.patch, self.prerelease, self.build)
        )


def parse(text):
    """把版本字符串解析成 :class:`Version`；不合法时抛 ``ValueError``。"""
    if not isinstance(text, str):
        raise ValueError("版本号必须是字符串：%r" % (text,))

    match = _SPEC.match(text)
    if match is None:
        raise ValueError("非法版本号：%r" % (text,))

    major, minor, patch = match.group(1), match.group(2), match.group(3)
    prerelease = match.group(4)
    build = match.group(5)

    parts = prerelease.split(".") if prerelease else []
    for ident in parts:
        if ident == "":
            raise ValueError("prerelease 标识符不能为空：%r" % (text,))
        if not _IDENT.match(ident):
            raise ValueError("prerelease 含非法字符：%r" % (text,))

    if build is not None:
        for ident in build.split("."):
            if ident == "":
                raise ValueError("build 标识符不能为空：%r" % (text,))
            if not _IDENT.match(ident):
                raise ValueError("build 含非法字符：%r" % (text,))

    return Version(int(major), int(minor), int(patch), parts, build)


def compare(left, right):
    """比较两个 ``Version``（或版本字符串），返回 ``-1`` / ``0`` / ``1``。"""
    if not isinstance(left, Version):
        left = parse(left)
    if not isinstance(right, Version):
        right = parse(right)
    return left.compare(right)


def sorted_versions(versions):
    """按大小升序排序；相等的版本保持输入顺序。"""
    items = [v if isinstance(v, Version) else parse(v) for v in versions]
    return sorted(items, key=_sort_key)


def _sort_key(version):
    return (
        version.major,
        version.minor,
        version.patch,
        ".".join(version.prerelease),
        version.build or "",
    )
