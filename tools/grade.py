#!/usr/bin/env python3
# ⚠️ 这个文件由 lab/sync_grader.py 从 lab/grade.py 复制而来。
#    要改请改 lab/ 下的那份，然后重新同步 —— 不要直接改这里。
"""grade.py —— 作业自查 / 验收引擎。

**学生和老师用的是同一份代码** —— 结果完全一样。
提交前自己跑一遍，看到 PASS 再交。

用法：

    python grade.py hw5 https://github.com/<用户名>/EC-Training-Labs
    python grade.py hw5 /path/to/local/repo
    python grade.py hw5 <repo> --json          # 机器可读
    python grade.py hw5 <repo> --ascii         # 终端画不出框线时用
    python grade.py --list                     # 看有哪些作业（按模块分组）

退出码：0 = PASS，1 = FAIL，2 = 出错（读不到仓库等）

---

这个文件**不认识任何一门课**：没有「HW5」，没有「cpp1」，没有工程路径。
它只做四件事：加载课程 → 逐个跑规则 → 渲染结果 → 退出码。

```text
grade.py           引擎：结果渲染 / 课程加载 / 命令行        ← 你在这里
rulelib/           可复用的规则库（git 规则、代码规则）
courses/           ★ 每门课一个文件，换课程只改这里
```

加一门课：在 `courses/` 里写一个 `.py`，里面给出：
  `MODULE`（英文短名，稳定）· `MODULE_TITLE`（给学生看的标题）· `LESSONS`
不用动这个文件，也不用动 `rulelib/`。

---

## 怎么改评分规则

规则就是**普通函数**：`f(repo, ...) -> Result`。
课程文件里用 `R(函数, 参数...)` 把参数绑上，引擎逐个 `rule(repo)` 调用。

**不要为了加一条规则去改引擎。** 现有手段（`rulelib/code.py`）：

| 想验什么 | 用哪条 |
| --- | --- |
| 它能不能编译 | `code.check_build(project)` |
| 行为对不对 | `code.check_tests(project, ["test_xxx"])` |
| 签名/类型对不对 | `code.check_contract(project, Path("probes/xxx.cpp"))` |
| 符号表对不对（inline / static / 未定义） | `code.check_symbol_kind(project, probe, "名字", "W")` |
| 风格 | `code.check_formatting(project, ["base"])` |
| 不许出现某个东西 | `code.check_no_token(project, ["double"], why="...")` |
| 有没有写回答 | `code.check_answers("day0/homework/answers.md")` |

还缺手段的话，先把规则写进 `rulelib/`（**它不能认识具体课程**），再在课程文件里用。
"""

from __future__ import annotations

import argparse
import importlib
import json
import os
import pkgutil
import re
import shutil
import subprocess
import sys
import tempfile
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from rulelib.base import Repo, RepoError, Result, enable_vt  # noqa: E402

# ══════════════════════════════════════════════════════════════════
# 课程加载
# ══════════════════════════════════════════════════════════════════


def load_courses() -> dict[str, tuple]:
    """把 `courses/` 下每个模块读进来。

    返回 {lesson_id: (模块id, 模块标题, 作业标题, [规则...], 选项)}。

    **模块 id 和标题是两个东西**：id 是稳定的英文短名（`cpp-basics`），
    给分组和 `--json` 的机器消费者用；标题是给学生看的（`C++ 基础 · 自学模块`）。
    原来只用了标题，于是 `MODULE` 这个常量在文档和两门课里都声明了、
    引擎却从来不读 —— 又一处「文档说了、实现没做」。

    课程文件坏了只跳过它自己 —— 一门课写错不该让另一门课也用不了。
    """
    import courses as pkg

    out: dict[str, tuple] = {}
    for info in pkgutil.iter_modules(pkg.__path__):
        if info.name.startswith("_"):
            continue
        try:
            mod = importlib.import_module(f"courses.{info.name}")
        except Exception as e:                       # noqa: BLE001
            print(f"!! 课程 {info.name} 加载失败：{type(e).__name__}: {e}",
                  file=sys.stderr)
            continue
        mid = getattr(mod, "MODULE", info.name)
        title = getattr(mod, "MODULE_TITLE", info.name)
        for lesson, entry in getattr(mod, "LESSONS", {}).items():
            if lesson in out:
                print(f"!! 作业编号重复：{lesson}（{info.name} 和 {out[lesson][0]}）",
                      file=sys.stderr)
            out[lesson] = (mid, title, *entry)
    return out


# ══════════════════════════════════════════════════════════════════
# 报告渲染
# ══════════════════════════════════════════════════════════════════

BOX_W = 62

# ANSI 颜色/加粗的转义序列。**算宽度时必须先去掉它** ——
# 否则 `\033[31m` 会被当成 5 个可见字符，整个框线全歪。
ANSI = re.compile(r"\033\[[0-9;]*m")


def _w(s: str) -> int:
    """字符串在终端里的显示宽度（CJK 算 2 列，ANSI 转义不算）。"""
    s = ANSI.sub("", s)
    return sum(2 if unicodedata.east_asian_width(c) in "WF" else 1 for c in s)


def _pad(s: str, width: int) -> str:
    return s + " " * max(0, width - _w(s))


def _clip(s: str, width: int) -> str:
    """按显示宽度截断（超出加省略号）。"""
    if _w(s) <= width:
        return s
    out, acc = "", 0
    for c in s:
        cw = 2 if unicodedata.east_asian_width(c) in "WF" else 1
        if acc + cw > width - 1:
            break
        out += c
        acc += cw
    return out + "…"


class Style:
    """支持退化成纯 ASCII（老终端画不出框线时）。"""

    def __init__(self, ascii_only: bool = False, color: bool = True):
        if ascii_only:
            self.tl, self.tr, self.bl, self.br = "+", "+", "+", "+"
            self.h, self.v, self.lt, self.rt = "-", "|", "+", "+"
            self.ok, self.no, self.wa, self.sk = "[OK]", "[!!]", "[--]", "[  ]"
        else:
            self.tl, self.tr, self.bl, self.br = "┌", "┐", "└", "┘"
            self.h, self.v, self.lt, self.rt = "─", "│", "├", "┤"
            self.ok, self.no, self.wa, self.sk = "✅", "❌", "⚠️", "○"
        self.color = color

    def _c(self, code: str, s: str) -> str:
        return f"\033[{code}m{s}\033[0m" if self.color else s

    def green(self, s: str) -> str:
        return self._c("32", s)

    def red(self, s: str) -> str:
        return self._c("31", s)

    def yellow(self, s: str) -> str:
        return self._c("33", s)

    def dim(self, s: str) -> str:
        return self._c("90", s)

    def bold(self, s: str) -> str:
        return self._c("1", s)


def render(title: str, meta: list[tuple[str, str]],
           results: list[Result], st: Style) -> str:
    inner = BOX_W - 2
    lines: list[str] = []
    # 所有宽度都用 _w() 算（CJK 算 2 列、ANSI 不算）。
    # **不能用 len()** —— "仓库" 是 2 个字符但占 4 列，用了 len() 框线就会歪。
    LIMIT = inner - 1                       # 内容区可用宽度

    lines.append(st.tl + st.h * inner + st.tr)
    lines.append(st.v + " " + _pad(st.bold(_clip(title, LIMIT)), LIMIT) + st.v)
    for k, v in meta:
        lines.append(st.v + " "
                     + _pad(f"{k} {_clip(v, LIMIT - _w(k) - 1)}", LIMIT) + st.v)
    lines.append(st.lt + st.h * inner + st.rt)

    for res in results:
        if res.skipped:
            mark = st.dim(st.sk)          # 跳过：既不是过也不是错，别占注意力
        elif res.ok:
            mark = st.green(st.ok)
        elif res.severity == "warn":
            mark = st.yellow(st.wa)
        else:
            mark = st.red(st.no)
        name = _clip(res.name, 22)
        # 明细的预算要从**真实标记宽度**倒推：
        #   `✅` 占 2 列、`[OK]` 占 4 列（--ascii 模式），差这 2 列就会顶破右边框
        budget = LIMIT - _w(mark) - 1 - 22 - 1
        line = f"{mark} {_pad(name, 22)} {_clip(res.detail, max(8, budget))}"
        lines.append(st.v + " " + _pad(line, LIMIT) + st.v)

    lines.append(st.lt + st.h * inner + st.rt)

    blocking = [r for r in results if r.blocking]
    verdict = "FAIL" if blocking else "PASS"
    vt = st.red(verdict) if blocking else st.green(verdict)
    if blocking:
        note = f"{len(blocking)} 项必修未通过"
    else:
        warn_n = sum(1 for r in results if r.severity == "warn" and not r.ok)
        note = "全部必修项通过" + (f"（{warn_n} 项提示）" if warn_n else "")
    head = f"结论   {vt}    "
    lines.append(st.v + " "
                 + _pad(head + _clip(note, LIMIT - _w(head)),
                        LIMIT) + st.v)
    lines.append(st.bl + st.h * inner + st.br)

    return "\n".join(lines)


# ══════════════════════════════════════════════════════════════════
# 入口
# ══════════════════════════════════════════════════════════════════


def resolve_repo(target: str, workdir: Path):
    """把命令行参数变成 (Repo, 显示用的地址)。"""
    if re.match(r"^(https?://|git@)", target):
        dest = workdir / "repo"
        r = subprocess.run(["git", "clone", "--quiet", target, str(dest)],
                           capture_output=True, text=True, encoding="utf-8",
                           errors="replace")
        if r.returncode != 0:
            raise RepoError(f"clone 失败：{(r.stderr or '').strip()[:200]}")
        # 有 upstream 就一并拉下来（Task 9 之后的学生仓库会有）
        subprocess.run(["git", "-C", str(dest), "fetch", "--quiet", "--all"],
                       capture_output=True)
        return Repo(dest), target
    return Repo(target), str(Path(target).resolve())


def run_rules(rules: list, repo: Repo, stop_on_fail: bool = False) -> list[Result]:
    """逐条跑规则。

    两件事：

    **① 一条规则崩了不该让整次验收崩掉** —— 记成一条错误，继续跑后面的。
    学生看到的应该是「这条查不了」，而不是一个 Python traceback。

    **② `stop_on_fail=True` 时，第一条必修项没过就停**，剩下的记成「跳过」。
    这是给「编译 → 测试 → 契约」这种有先后顺序的课用的：
    编译都没过的时候，后面每一条都会跟着红，而真正要修的只有第一条。
    默认关闭 —— Git 那类互相独立的检查要全部跑完，学生一次看到所有问题。
    """
    out: list[Result] = []
    for i, rule in enumerate(rules):
        if stop_on_fail and any(r.blocking for r in out):
            for rest in rules[i:]:
                out.append(Result.skip(_rule_name(rest)))
            break
        try:
            res = rule(repo)
        except RepoError:
            raise
        except Exception as e:                       # noqa: BLE001
            out.append(Result(_rule_name(rule)[:20], False,
                              f"检查出错：{type(e).__name__}: {e}"))
            continue
        if isinstance(res, list):
            out += res
        else:
            out.append(res)
    return out


def _rule_name(rule) -> str:
    return str(getattr(rule, "__name__", None) or rule)


def main() -> int:
    # Windows 终端默认可能是 GBK，先切 UTF-8，否则中文和框线会乱
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")     # type: ignore[attr-defined]
        except Exception:
            pass

    ap = argparse.ArgumentParser(
        description="作业自查 / 验收工具",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("lesson", nargs="?", help="作业编号，如 hw5 / cpp1")
    ap.add_argument("repo", nargs="?", help="仓库地址（URL）或本地路径")
    ap.add_argument("--json", action="store_true", help="输出 JSON")
    ap.add_argument("--ascii", action="store_true", help="用纯 ASCII 边框")
    ap.add_argument("--no-color", action="store_true",
                    help="不要颜色（重定向到文件时自动关闭）")
    ap.add_argument("--color", action="store_true",
                    help="强制上色（终端检测不出来时用）")
    ap.add_argument("--list", action="store_true", help="列出所有作业")
    ap.add_argument("--clang-format", dest="clang_format", default=None,
                    help="clang-format 可执行文件路径（没装在 PATH 上时用）")
    args = ap.parse_args()

    lessons = load_courses()

    if args.list or not args.lesson:
        by_module: dict[str, tuple[str, list[tuple[str, str]]]] = {}
        for lid, entry in lessons.items():
            mid, mtitle, name = entry[0], entry[1], entry[2]
            by_module.setdefault(mid, (mtitle, []))[1].append((lid, name))
        print("可用的作业：")
        for mid in sorted(by_module):
            mtitle, items = by_module[mid]
            print(f"\n  【{mtitle}】")
            for lid, name in sorted(items):
                print(f"    {lid:6s} {name}")
        print()
        return 0

    if args.lesson not in lessons:
        print(f"!! 没有这个作业：{args.lesson}", file=sys.stderr)
        print(f"   可用：{', '.join(sorted(lessons))}", file=sys.stderr)
        return 2
    if not args.repo:
        print("!! 还要给一个仓库地址或路径", file=sys.stderr)
        return 2

    entry = lessons[args.lesson]
    module, module_title, title, rules = entry[0], entry[1], entry[2], entry[3]
    opts = entry[4] if len(entry) > 4 else {}
    if args.clang_format:
        # 引擎不认识 clang-format，也不该认识；规则库自己会读这个变量
        import os
        os.environ["CLANG_FORMAT"] = args.clang_format
    tmp = Path(tempfile.mkdtemp(prefix="ectl-grade-"))
    try:
        repo, shown = resolve_repo(args.repo, tmp)
        branch = repo.current_branch()
        # 课程可以声明自己需要 clang-format；没有就让它自己在 PATH 上找
        results = run_rules(rules, repo, stop_on_fail=bool(opts.get("stop_on_fail")))
    except RepoError as e:
        print(f"!! {e}", file=sys.stderr)
        return 2
    except Exception as e:                     # noqa: BLE001
        print(f"!! 检查过程中出错：{type(e).__name__}: {e}", file=sys.stderr)
        return 2
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    if args.json:
        print(json.dumps({
            "lesson": args.lesson,
            "module": module,
            "module_title": module_title,
            "repo": shown,
            "branch": branch,
            "verdict": "FAIL" if any(r.blocking for r in results) else "PASS",
            "results": [{"name": r.name, "ok": r.ok, "detail": r.detail,
                         "severity": r.severity} for r in results],
        }, ensure_ascii=False, indent=2))
    else:
        # 颜色开关：--color 强制开，--no-color 强制关；
        # 都没有的话看"这是个终端吗" + "这个终端认不认 ANSI"
        if args.color:
            color = True
        elif args.no_color or not sys.stdout.isatty():
            color = False
        else:
            color = enable_vt()
        st = Style(ascii_only=args.ascii, color=color)
        print()
        print(render(title, [("仓库", shown), ("分支", branch)], results, st))
        print()

        blocking = [r for r in results if r.blocking]
        if blocking:
            print("必修项没过：")
            for r in blocking:
                print(f"  · {r.name}：{r.detail}")
            print()
            print("改完再跑一次这个命令，看到 PASS 再提交。")

    return 1 if any(r.blocking for r in results) else 0


if __name__ == "__main__":
    sys.exit(main())
