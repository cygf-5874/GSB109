#!/usr/bin/env python3
"""semvercmp 的固定验收程序。

场景（10 个）：basic 1 + pre 3 + build 1 + stable 1 + validate 2 + scale 2。

本文件属于固定判据，解题方不得修改。所有判据都是确定性的：
不使用 ``random``、不使用 ``time``、不依赖 ``dict`` 迭代顺序。
"""

import argparse
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from semvercmp import parse, sorted_versions  # noqa: E402


def _verdict(ok, expected, actual):
    return (bool(ok), expected, actual)


def _texts(versions):
    return [version.text() for version in versions]


# --------------------------------------------------------------------------
# scale 组：长数字标识符与大规模稳定排序
# --------------------------------------------------------------------------

def scenario_scale_big_numeric_identifiers():
    shorter = "9" * 99999
    longer = "1" + ("0" * 99999)
    left = parse("1.0.0-a." + shorter)
    right = parse("1.0.0-a." + longer)
    if not (left < right):
        return _verdict(False, "100000 位数值标识符按数值比较", "99999 位 9 被当成更大")
    if not (right > left):
        return _verdict(False, "反向比较一致", "为假")
    if hash(parse("1.0.0+" + shorter)) != hash(parse("1.0.0+b")):
        return _verdict(False, "build 不影响哈希", "哈希不同")
    return _verdict(True, "长数值标识符不转 int 也能正确比较", "一致")


def scenario_scale_stable_sorting():
    n = 20000
    raw = ["1.0.0-rc.%d+b%d" % (i, i) for i in range(n)]
    got = _texts(sorted_versions([parse(text) for text in raw]))
    if got != raw:
        for i, (a, b) in enumerate(zip(got, raw)):
            if a != b:
                return _verdict(False, "大规模稳定排序保持输入顺序", "首个差异 index=%d: %r != %r" % (i, a, b))
        return _verdict(False, "大规模稳定排序保持输入顺序", "长度或顺序不一致")
    return _verdict(True, "20000 个版本稳定排序", "一致")

# --------------------------------------------------------------------------
# basic 组：三段数值比较
# --------------------------------------------------------------------------

def scenario_basic_three_part_numeric():
    version = parse("1.2.3")
    if (version.major, version.minor, version.patch) != (1, 2, 3):
        return _verdict(False, "字段 = 1/2/3",
                        "字段 = %r/%r/%r" % (version.major, version.minor, version.patch))
    plain = parse("v1.2.3")
    if (plain.major, plain.minor, plain.patch) != (1, 2, 3):
        return _verdict(False, "前导 v 可选，v1.2.3 -> 1/2/3",
                        "v1.2.3 -> %r/%r/%r" % (plain.major, plain.minor, plain.patch))
    chain = parse("1.2.3") < parse("1.2.4") < parse("1.3.0") < parse("2.0.0")
    reverse = parse("2.0.0") > parse("1.3.0") > parse("1.2.4") > parse("1.2.3")
    if not (chain and reverse):
        return _verdict(False, "1.2.3 < 1.2.4 < 1.3.0 < 2.0.0",
                        "链式比较 = %r / %r" % (chain, reverse))
    return _verdict(True, "字段与前导 v 正确，三段数值严格递增", "一致")


# --------------------------------------------------------------------------
# pre 组：预发布版的比较规则
# --------------------------------------------------------------------------

def scenario_pre_release_above_prerelease():
    rc = parse("1.0.0-rc.1")
    release = parse("1.0.0")
    if not (rc < release):
        return _verdict(False, "1.0.0-rc.1 < 1.0.0", "1.0.0-rc.1 < 1.0.0 为假")
    if not (release > rc):
        return _verdict(False, "1.0.0 > 1.0.0-rc.1", "1.0.0 > 1.0.0-rc.1 为假")
    bigger = parse("2.0.0-alpha") > parse("1.9.9")
    if not bigger:
        return _verdict(False, "2.0.0-alpha > 1.9.9", "为假")
    return _verdict(True, "带 prerelease 的版本低于同号发布版", "一致")


def scenario_pre_identifier_wise():
    if not (parse("1.0.0-rc.2") < parse("1.0.0-rc.10")):
        return _verdict(False, "1.0.0-rc.2 < 1.0.0-rc.10", "为假（数字标识符应按数值比）")
    if not (parse("1.0.0-alpha.1") < parse("1.0.0-alpha.beta")):
        return _verdict(False, "1.0.0-alpha.1 < 1.0.0-alpha.beta", "为假（字母标识符按 ASCII 比）")
    if not (parse("1.0.0-1") < parse("1.0.0-alpha")):
        return _verdict(False, "1.0.0-1 < 1.0.0-alpha", "为假（纯数字标识符排在字母前）")
    if not (parse("1.0.0-1.2.3") < parse("1.0.0-1.2.4")):
        return _verdict(False, "1.0.0-1.2.3 < 1.0.0-1.2.4", "为假")
    if not (parse("1.0.0-rc.10") > parse("1.0.0-rc.2")):
        return _verdict(False, "1.0.0-rc.10 > 1.0.0-rc.2", "为假")
    return _verdict(True, "prerelease 按标识符逐个比较", "一致")


def scenario_pre_shorter_is_smaller():
    if not (parse("1.0.0-alpha") < parse("1.0.0-alpha.1")):
        return _verdict(False, "1.0.0-alpha < 1.0.0-alpha.1", "为假")
    if not (parse("1.0.0-alpha.1") > parse("1.0.0-alpha")):
        return _verdict(False, "1.0.0-alpha.1 > 1.0.0-alpha", "为假")
    if not (parse("1.0.0-1") < parse("1.0.0-1.0")):
        return _verdict(False, "1.0.0-1 < 1.0.0-1.0", "为假")
    return _verdict(True, "前缀相同时标识符少的更小", "一致")


# --------------------------------------------------------------------------
# build 组：build metadata 不参与比较
# --------------------------------------------------------------------------

def scenario_build_metadata_ignored():
    left = parse("1.0.0+build.1")
    right = parse("1.0.0+build.2")
    if left.compare(right) != 0:
        return _verdict(False, "compare(1.0.0+build.1, 1.0.0+build.2) == 0",
                        "= %r" % (left.compare(right),))
    if left < right or right < left:
        return _verdict(False, "build 不同的同号版本互不小于", "出现了大小关系")
    if parse("1.2.3+build.7").build != "build.7":
        return _verdict(False, "build 被保留", "= %r" % (parse("1.2.3+build.7").build,))
    order = _texts(sorted_versions([parse("1.0.0+z"), parse("1.0.0+a")]))
    if order != ["1.0.0+z", "1.0.0+a"]:
        return _verdict(False, "build 不同的同号版本保持输入顺序：['1.0.0+z', '1.0.0+a']",
                        "= %r" % (order,))
    return _verdict(True, "build metadata 不参与比较、且被保留", "一致")


# --------------------------------------------------------------------------
# stable 组：排序稳定
# --------------------------------------------------------------------------

def scenario_stable_equal_keep_order():
    raw = ["1.0.0-alpha", "1.0.0-alpha.1", "1.0.0-alpha"]
    got = _texts(sorted_versions([parse(text) for text in raw]))
    expected = ["1.0.0-alpha", "1.0.0-alpha", "1.0.0-alpha.1"]
    if got != expected:
        return _verdict(False, "排序后 %r" % (expected,), "= %r" % (got,))
    return _verdict(True, "相等版本保持输入顺序", "一致")


# --------------------------------------------------------------------------
# validate 组：非法输入与哈希一致性
# --------------------------------------------------------------------------

ILLEGAL = [
    "1.2",
    "1.2.3.4",
    "1.01.0",
    "1.0.0-alpha..1",
    "1.0.0-alpha_1",
    "1.0.0-",
    "1.0.0+",
    "x.y.z",
]


def scenario_validate_rejects_illegal():
    for text in ILLEGAL:
        try:
            value = parse(text)
        except ValueError:
            continue
        except Exception as exc:  # noqa: BLE001
            return _verdict(False, "parse(%r) 抛 ValueError" % text,
                            "抛 %s: %s" % (type(exc).__name__, exc))
        return _verdict(False, "parse(%r) 抛 ValueError" % text, "返回了 %r" % (value,))
    return _verdict(True, "全部非法输入都抛 ValueError", "一致")


def scenario_validate_hash_eq_consistent():
    left = parse("1.0.0+build.1")
    right = parse("1.0.0+build.2")
    if not (left == right):
        return _verdict(False, "1.0.0+build.1 == 1.0.0+build.2", "为假")
    if not (right == left):
        return _verdict(False, "1.0.0+build.2 == 1.0.0+build.1", "为假")
    if hash(left) != hash(right):
        return _verdict(False, "hash(1.0.0+build.1) == hash(1.0.0+build.2)",
                        "%r != %r" % (hash(left), hash(right)))
    table = {left: "ok"}
    if table.get(right) != "ok":
        return _verdict(False, "相等的版本可以互相作为 dict 键", "查不到另一把键")
    return _verdict(True, "相等与哈希一致、可作 dict 键", "一致")


SCENARIOS = (
    ("basic", "three-part-numeric", scenario_basic_three_part_numeric),
    ("pre", "release-above-prerelease", scenario_pre_release_above_prerelease),
    ("pre", "identifier-wise", scenario_pre_identifier_wise),
    ("pre", "shorter-is-smaller", scenario_pre_shorter_is_smaller),
    ("build", "metadata-ignored", scenario_build_metadata_ignored),
    ("stable", "equal-keep-order", scenario_stable_equal_keep_order),
    ("validate", "rejects-illegal", scenario_validate_rejects_illegal),
    ("validate", "hash-eq-consistent", scenario_validate_hash_eq_consistent),
    ("scale", "big-numeric-identifiers", scenario_scale_big_numeric_identifiers),
    ("scale", "stable-sorting", scenario_scale_stable_sorting),
)


def main(argv=None):
    parser = argparse.ArgumentParser(prog="check.py")
    parser.add_argument("-list", dest="list_scenarios", action="store_true",
                        help="列出全部场景后退出")
    parser.add_argument("--only", dest="only", default=None,
                        help="只运行指定组")
    args = parser.parse_args(argv)

    if args.list_scenarios:
        for group, name, _func in SCENARIOS:
            print("%s/%s" % (group, name))
        return 0

    selected = [s for s in SCENARIOS if args.only is None or s[0] == args.only]
    passed = 0
    for group, name, func in selected:
        try:
            ok, expected, actual = func()
        except Exception as exc:  # noqa: BLE001
            ok, expected, actual = False, "无异常", "%s: %s" % (type(exc).__name__, exc)
        if ok:
            passed += 1
            print("PASS %s/%s" % (group, name))
        else:
            print("FAIL %s/%s  期望=%s 实际=%s" % (group, name, expected, actual))

    print("结果：通过 %d/%d" % (passed, len(selected)))
    return 0 if selected and passed == len(selected) else 1


if __name__ == "__main__":
    sys.exit(main())
