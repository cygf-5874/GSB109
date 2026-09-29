# semvercmp

`semvercmp` 是一个纯标准库的**语义化版本（SemVer）解析与比较**小库。

- 语言 / 运行：Python 3，只用标准库（`unittest` 跑用例），无第三方依赖。
- 自检：`scripts/check.sh`（内部调用 `check/check.py`，那是固定验收程序，**别改**）。
- 目录：

  ```
  semvercmp.py            解析、比较、排序（唯一实现文件）
  tests/test_semver.py    既有用例（14 个；只覆盖 1.2.3 与短 prerelease）
  repro.py                调用方给的最小复现
  check/check.py          固定验收程序：8 个场景
  ```

## 语言版本前提

- Python 3（开发与验证用 3.13）。
- **只用标准库**，不引入任何第三方依赖。

## 怎么跑

```bash
python3 -m unittest discover -s tests   # 既有用例，当前 14/14 全绿
python3 repro.py                        # 调用方给的最小复现
bash scripts/check.sh                   # 固定验收；支持 -list 与 --only <组名>
```

## 对外保证

下面 8 条是 `semvercmp` 的**对外契约**，实现必须全部守住；它们是本题验收点的唯一出处。

1. **解析**：`parse(text: str) -> Version` 接受 `MAJOR.MINOR.PATCH[-prerelease][+build]`，
   其中 `MAJOR`/`MINOR`/`PATCH` 是十进制非负整数，前导 `v` 可有可无。
2. **主次版本比较**：先比 `major`、再比 `minor`、再比 `patch`，按数值大小。
3. **预发布版更低**：带 prerelease 的版本**小于**同号的不带 prerelease 的版本
   （`1.0.0-rc.1 < 1.0.0`）。
4. **prerelease 逐标识符比较**：以 `.` 分隔的标识符从左到右逐个比较 ——
   纯数字标识符按数值比，含字母的标识符按 ASCII 字典序比，**纯数字 < 含字母**；
   若前缀相同，标识符个数少的那个更小（`1.0.0-alpha < 1.0.0-alpha.1`）。
5. **build metadata 不参与比较**：`+` 之后的内容既不参与大小比较、也不影响相等判断，
   但必须原样保留在 `Version` 对象里（`parse("1.2.3+build.7").build == "build.7"`）。
6. **排序稳定**：`sorted_versions(versions) -> list` 使用稳定的排序；
   按上面的规则相等（即 precedence 相同）的版本，保持它们在输入里的相对顺序。
7. **非法输入报错**：缺段（`1.2`）、数值段前导 0（`1.01.0`）、空标识符（`1.0.0-alpha..1`）、
   非法字符（`1.0.0-alpha_1`）、只有分隔符没有内容（`1.0.0-`、`1.0.0+`）都要抛 `ValueError`。
8. **可哈希且与相等一致**：`Version` 可以作为 `dict` 的键；`__eq__` 与比较结果一致
   —— 按第 5 条，`parse("1.0.0+a") == parse("1.0.0+b")` 为 `True`，
   它们的 `hash()` 也必须相同。
9. **任意长度数值标识符**：prerelease 里的纯数字标识符可以有 100,000 位以上；比较必须按
   数值语义（先比有效长度，再比数字字典序），**不得**用 `int()` / `float()` 或正则捕获组转数值，
   也不得因 Python 的整数转换位数限制而报错。
10. **稳定且可扩展**：`sorted_versions()` 对 20,000 个 precedence 相等的版本仍必须稳定；
    实现不得把全部 prerelease 标识符反复拼接成新的大字符串，也不得用 O(n²) 的冒泡式比较。
## 固定验收

```bash
python3 check/check.py          # 也支持 -list 与 --only <组>
```

`check/` 是固定验收程序，只按上面 8 条保证逐场景核验，**勿改**。
