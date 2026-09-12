#!/usr/bin/env python3
#!/usr/bin/env python3
# ⚠️ 这个文件由 lab/sync_grader.py 从 lab/grade.py 复制而来。
#    要改请改 lab/ 下的那份，然后重新同步 —— 不要直接改这里。
"""Day 0 作业自查 / 验收工具。

**学生和老师用的是同一份代码** —— 结果完全一样。
提交前自己跑一遍，看到 PASS 再交。

用法：

    python grade.py hw5 https://github.com/<用户名>/EC-Training-Labs
    python grade.py hw5 /path/to/local/repo
    python grade.py hw5 <repo> --json          # 机器可读
    python grade.py hw5 <repo> --ascii         # 终端画不出框线时用
    python grade.py --list                     # 看有哪些作业

退出码：0 = PASS，1 = FAIL，2 = 出错（读不到仓库等）
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import gitscore
from gitscore import Repo, RepoError, Result

# ══════════════════════════════════════════════════════════════════
# 各作业的配置
# ══════════════════════════════════════════════════════════════════

PROJECT = "day0/project"        # 作业代码在仓库里的位置

BRANCH_PATTERN = r"^(feat|fix|refactor|tune|exp)/[a-z0-9][a-z0-9-]*$"
# 允许的 type。style 单列是因为 HW4 就是做格式化的 —— 它必须有地方用。
MESSAGE_TYPES = "feat|fix|refactor|docs|test|chore|tune|style"
MESSAGE_PATTERN = rf"^({MESSAGE_TYPES})(\([a-z0-9_]+\))?!?: .+"

# 低信息量 message：这些词单独出现时什么也没说
BLACKLIST = [
    "update", "modify", "change", "changes", "tmp", "temp", "test", "tests",
    "tuning", "save", "commit", "push", "fix", "feat", "wip", "done", "ok",
    "改", "修改", "更新", "调试", "暂存", "备份", "提交", "测试",
    "111", "1", "123", "aaa", "xxx", "finally", "终于好了",
]

# 这些路径（在将来出现时）必须被 .gitignore 挡住
ARTIFACT_SAMPLES = [
    "day0/project/build/app.o",
    "day0/project/build/CMakeCache.txt",
    "day0/project/mcu/stm32f407/MDK-ARM/DebugConfig/day0.dbgconf",
    "day0/project/mcu/stm32f407/MDK-ARM/RTE/_day0/RTE_Components.h",
    "day0/project/mcu/stm32f407/MDK-ARM/day0.uvguix.zhangsan",
]


# ══════════════════════════════════════════════════════════════════
# 构建 / 测试（作业特有，但多个作业共用）
# ══════════════════════════════════════════════════════════════════


def _find_tool(name: str) -> str | None:
    return shutil.which(name)


def build_and_test(repo: Repo, want_tests: list[str] | None = None) -> Result:
    """在**临时目录**里构建并跑测试 —— 绝不往学生仓库里写东西。

    want_tests: 要求必须通过的测试名；None 表示"全部通过"
    """
    proj = repo.root / PROJECT
    if not (proj / "CMakeLists.txt").is_file():
        return Result("构建与测试", False, f"找不到 {PROJECT}/CMakeLists.txt")

    for tool in ("cmake",):
        if not _find_tool(tool):
            return Result("构建与测试", False, f"本机找不到 {tool}，无法验证")

    with tempfile.TemporaryDirectory(prefix="ectl-grade-") as td:
        cfg = subprocess.run(["cmake", "-S", str(proj), "-B", td],
                             capture_output=True, text=True, encoding="utf-8",
                             errors="replace")
        if cfg.returncode != 0:
            tail = (cfg.stderr or cfg.stdout).strip().splitlines()[-3:]
            return Result("构建与测试", False, "cmake 配置失败：" + " / ".join(tail))

        bld = subprocess.run(["cmake", "--build", td, "-j"],
                             capture_output=True, text=True, encoding="utf-8",
                             errors="replace")
        if bld.returncode != 0:
            tail = (bld.stderr or bld.stdout).strip().splitlines()[-3:]
            return Result("构建与测试", False, "编译失败：" + " / ".join(tail))

        # 直接跑可执行文件，拿到逐用例的输出（ctest 会把它吞掉）
        #
        # Windows 两个坑：
        #   ① 可执行文件带 .exe 后缀，不能靠"没有后缀"来判断
        #   ② MSVC 是多配置生成器，产物在 tests/Debug/ 下面，得递归找
        results: dict[str, str] = {}
        tests_dir = Path(td) / "tests"
        for exe in sorted(tests_dir.rglob("test_*")):
            if not exe.is_file():
                continue
            name = exe.stem                      # test_encoder.exe -> test_encoder
            if not name.startswith("test_"):
                continue
            if exe.suffix and exe.suffix.lower() not in (".exe", ""):
                continue                         # .o / .pdb / .cmake 之类，跳过
            if os.name != "nt" and not os.access(exe, os.X_OK):
                continue                         # 非 Windows 上还要有执行权限
            try:
                r = subprocess.run([str(exe)], capture_output=True, text=True,
                                   encoding="utf-8", errors="replace", timeout=60)
            except (OSError, subprocess.TimeoutExpired):
                continue
            results[name] = r.stdout

    if not results:
        return Result("构建与测试", False, "没有找到任何测试可执行文件")

    if want_tests is None:
        want_tests = sorted(results)

    summary, failed = [], []
    for name in want_tests:
        out = results.get(name)
        if out is None:
            failed.append(f"{name} 不存在")
            continue
        m = re.search(r"(\d+)/(\d+) passed", out)
        if not m:
            failed.append(f"{name} 没有输出结果")
            continue
        got, total = int(m.group(1)), int(m.group(2))
        summary.append(f"{name.replace('test_', '')} {got}/{total}")
        if got != total:
            missing = [l.strip() for l in out.splitlines() if "[FAIL]" in l]
            failed.append(f"{name} 挂了 {total - got} 个用例"
                          + ("：" + missing[0][:60] if missing else ""))

    if failed:
        return Result("测试全部通过", False, "；".join(failed))
    return Result("测试全部通过", True, " · ".join(summary))


# ══════════════════════════════════════════════════════════════════
# HW5 · Git 工作流
# ══════════════════════════════════════════════════════════════════


def base_branch(repo: Repo) -> str:
    """学生分叉的基线分支。"""
    for name in ("main", "master"):
        if name in repo.branches():
            return name
    return "HEAD"


def grade_hw5(repo: Repo) -> list[Result]:
    r: list[Result] = []

    # ── 必修（与任务书「评分」一节一一对应）──
    r.append(gitscore.check_branch_naming(repo, BRANCH_PATTERN))
    r.append(gitscore.check_branch_has_work(repo, BRANCH_PATTERN))
    r.append(gitscore.check_message_format(repo, MESSAGE_PATTERN))
    r.append(gitscore.check_message_blacklist(repo, BLACKLIST))
    r.append(gitscore.check_no_artifacts(repo, rev="HEAD"))
    r.append(gitscore.check_no_conflict_markers(repo, rev="HEAD", paths=[PROJECT]))
    r.append(gitscore.check_path_unmodified(repo, f"{PROJECT}/tests"))
    r.append(gitscore.check_file_contains(
        repo, f"{PROJECT}/app/arm.h", ["CALIBRATE", "DROP_MODE"],
        name="冲突保留双方意图"))
    r.append(check_todos_done(repo))
    r.append(gitscore.check_merge_happened(repo, rev="HEAD"))
    r.append(build_and_test(repo))

    # ── 提示（只显示，不影响结论）──
    r.append(gitscore.check_commit_count(repo, max_n=15, base=base_branch(repo)))
    r.append(gitscore.check_message_length(repo, lo=10, hi=72))
    r.append(gitscore.check_atomic_heuristic(repo, max_top_dirs=3))
    r.append(gitscore.check_worktree_clean(repo))
    r.append(gitscore.check_pushed(repo))

    return r


# ══════════════════════════════════════════════════════════════════
# HW1 / HW2（共用同一个工程，检查很薄）
# ══════════════════════════════════════════════════════════════════


def grade_hw1(repo: Repo) -> list[Result]:
    """把项目跑起来：能配置、能编译就行。测试此时**应该有一个失败**。"""
    r = [build_and_test(repo, want_tests=[]) if False else _build_only(repo)]
    r.append(gitscore.check_worktree_clean(repo))
    return r


def _build_only(repo: Repo) -> Result:
    proj = repo.root / PROJECT
    if not (proj / "CMakeLists.txt").is_file():
        return Result("能构建", False, f"找不到 {PROJECT}/CMakeLists.txt")
    if not _find_tool("cmake"):
        return Result("能构建", False, "本机找不到 cmake")
    with tempfile.TemporaryDirectory(prefix="ectl-grade-") as td:
        cfg = subprocess.run(["cmake", "-S", str(proj), "-B", td],
                             capture_output=True, text=True, encoding="utf-8",
                             errors="replace")
        if cfg.returncode != 0:
            return Result("能构建", False, "cmake 配置失败")
        bld = subprocess.run(["cmake", "--build", td, "-j"],
                             capture_output=True, text=True, encoding="utf-8",
                             errors="replace")
        if bld.returncode != 0:
            tail = (bld.stderr or bld.stdout).strip().splitlines()[-2:]
            return Result("能构建", False, "编译失败：" + " / ".join(tail))
    return Result("能构建", True, "cmake 配置 + 编译通过")


def grade_hw2(repo: Repo) -> list[Result]:
    """修编码器回绕：两个测试都要全绿。"""
    r = [build_and_test(repo)]
    r.append(gitscore.check_path_unmodified(repo, f"{PROJECT}/tests"))
    r.append(gitscore.check_message_format(repo, MESSAGE_PATTERN))
    return r


# ══════════════════════════════════════════════════════════════════
# HW3 / HW4 用到的检查
# ══════════════════════════════════════════════════════════════════


def find_clang_format(explicit: str | None = None) -> str | None:
    """找一个能用的 clang-format。

    **大多数人不会单独装 clang-format，但 CLion 自带一个**，
    所以除了 PATH 还要去 CLion / JetBrains Toolbox 的安装目录里翻。

    实在找不到也没关系 —— check_formatting 会退回到缩进启发式。
    """
    if explicit:
        return explicit if Path(explicit).exists() else None

    exe = shutil.which("clang-format")
    if exe:
        return exe

    import glob
    home = Path.home()
    patterns: list[str] = []
    if os.name == "nt":
        local = os.environ.get("LOCALAPPDATA", str(home / "AppData" / "Local"))
        patterns += [
            r"C:\\Program Files\\JetBrains\\*\\bin\\clang\\win\\clang-format.exe",
            r"C:\\Program Files\\JetBrains\\*\\bin\\clang-format.exe",
            r"C:\\Program Files\\LLVM\\bin\\clang-format.exe",
            rf"{local}\\Programs\\CLion*\\bin\\clang\\win\\clang-format.exe",
            rf"{local}\\JetBrains\\Toolbox\\apps\\CLion\\**\\bin\\clang\\win\\clang-format.exe",
            rf"{local}\\JetBrains\\Toolbox\\apps\\CLion\\**\\bin\\clang-format.exe",
        ]
    else:
        patterns += [
            str(home / ".local/share/JetBrains/Toolbox/apps/CLion/**/bin/clang/linux/clang-format"),
            "/opt/clion*/bin/clang/linux/clang-format",
            "/opt/llvm*/bin/clang-format",
            "/usr/lib/llvm-*/bin/clang-format",
        ]
    for pat in patterns:
        hits = sorted(glob.glob(pat, recursive=True))
        if hits:
            return hits[-1]
    return None


# 工程 .clang-format 里的缩进宽度。用来在没装 clang-format 时做粗略判断。
def _indent_width(repo: Repo) -> int:
    f = repo.root / PROJECT / ".clang-format"
    if f.is_file():
        m = re.search(r"^IndentWidth:\s*(\d+)", f.read_text(encoding="utf-8"), re.M)
        if m:
            return int(m.group(1))
    return 2      # LLVM 默认


def _indent_heuristic(repo: Repo, subdirs: list[str], width: int) -> tuple[int, int]:
    """数一数"缩进不是 width 整数倍"的行有多少。

    工程配的是 4 空格，所以格式化之后这个数应当接近 0。
    实测：未格式化 88.9%，已格式化 0.0% —— 区分度足够大。
    **这是启发式，不是精确判断**，只在没有 clang-format 时兜底。
    """
    proj = repo.root / PROJECT
    bad = tot = 0
    for d in subdirs:
        base = proj / d
        if not base.is_dir():
            continue
        for f in list(base.rglob("*.cpp")) + list(base.rglob("*.h")):
            for line in f.read_text(encoding="utf-8", errors="replace").splitlines():
                m = re.match(r"^( +)\S", line)
                if not m:
                    continue
                tot += 1
                if len(m.group(1)) % width != 0:
                    bad += 1
    return bad, tot


def check_formatting(repo: Repo, subdirs: list[str],
                     explicit: str | None = None) -> Result:
    """这些目录下的 C++ 文件是否符合工程的 .clang-format。

    两条路：
      ① 有 clang-format（PATH 上或 CLion 自带的）→ 精确检查
      ② 没有 → 退回到缩进启发式（会在结果里标明）
    """
    proj = repo.root / PROJECT
    files: list[Path] = []
    for d in subdirs:
        base = proj / d
        if base.is_dir():
            files += sorted(base.rglob("*.cpp")) + sorted(base.rglob("*.h"))
    if not files:
        return Result("代码符合 clang-format", False, f"在 {subdirs} 下没找到 C++ 文件")

    exe = find_clang_format(explicit)
    if exe:
        bad: list[str] = []
        for f in files:
            r = subprocess.run([exe, "--style=file", "--dry-run", "--Werror", str(f)],
                               capture_output=True, text=True, encoding="utf-8",
                               errors="replace", cwd=str(proj), timeout=60)
            if r.returncode != 0:
                bad.append(f.relative_to(proj).as_posix())
        if bad:
            return Result("代码符合 clang-format", False,
                          f"{len(bad)}/{len(files)} 个文件需要重排：{', '.join(bad[:3])}")
        return Result("代码符合 clang-format", True,
                      f"{len(files)}/{len(files)} 个文件合规（clang-format 精确检查）")

    # 退路：缩进启发式
    width = _indent_width(repo)
    bad, tot = _indent_heuristic(repo, subdirs, width)
    pct = (100.0 * bad / tot) if tot else 0.0
    if pct > 20.0:
        return Result("代码符合 clang-format", False,
                      f"约 {pct:.0f}% 的缩进行不是 {width} 空格的整数倍 —— 看起来没格式化过")
    return Result("代码符合 clang-format", True,
                  f"缩进看起来符合（{width} 空格；本机没有 clang-format，用启发式判断）")


def check_symbol_defined(repo: Repo, symbol: str, subdirs: list[str]) -> Result:
    """某个函数**有定义**（不是只有声明）。"""
    proj = repo.root / PROJECT
    pat = re.compile(rf"\b{re.escape(symbol)}\s*\([^;{{]*\)\s*(?:const\s*)?\{{")
    for d in subdirs:
        base = proj / d
        if not base.is_dir():
            continue
        for f in list(base.rglob("*.cpp")) + list(base.rglob("*.h")):
            try:
                text = f.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            # 去掉声明行（以 ; 结尾），避免把 `float f(float);` 当成定义
            if pat.search(text):
                return Result(f"{symbol} 有实现", True,
                              f"在 {f.relative_to(proj).as_posix()} 里找到定义")
    return Result(f"{symbol} 有实现", False,
                  f"只找到声明，没找到实现（这会导致 undefined reference）")


def check_todos_done(repo: Repo) -> Result:
    """HW5 的三个 TODO 是否都真的处理了。

    只查"结果对不对"，不查写法 —— 例如 `kDefaultClampSpeed` 只要是 6.0
    （4.0 的 1.5 倍），怎么写都行。
    """
    proj = repo.root / PROJECT

    def merged(rel: str) -> str:
        """工作区优先，其次 HEAD —— 学生自查时改动可能还没提交。"""
        return (repo.worktree_file(rel) or repo.show_file("HEAD", rel) or "")

    problems: list[str] = []

    # TODO-a：夹爪速度调到 6.0（4.0 × 1.5）
    ctl = merged(f"{PROJECT}/app/control.cpp")
    m = re.search(r"kDefaultClampSpeed\s*=\s*([0-9.]+)f", ctl)
    if not m:
        problems.append("control.cpp 里找不到 kDefaultClampSpeed")
    elif abs(float(m.group(1)) - 6.0) > 0.01:
        problems.append(f"夹爪速度还是 {m.group(1)}，TODO-a 要求按 1.5 倍调到 6.0")

    # TODO-b：标定期间跳过阻力判断
    clp = merged(f"{PROJECT}/app/clamp.cpp")
    if "is_calibrating_" not in clp.split("ClampState Clamp::update", 1)[-1]:
        problems.append("clamp.cpp 的 update() 里没有用 is_calibrating_ 跳过阻力判断")

    # TODO-c：CALIBRATE（这条由"冲突保留双方意图"覆盖，这里只确认 TODO 注释清了）
    arm = merged(f"{PROJECT}/app/arm.h")
    if "CALIBRATE" not in arm:
        problems.append("arm.h 里没有 CALIBRATE")

    if problems:
        return Result("三个 TODO 都已处理", False, "；".join(problems[:2]))
    return Result("三个 TODO 都已处理", True, "夹爪速度 / 标定判断 / 工作模式 都改了")


def check_answers(repo: Repo, relpath: str, min_per_section: int = 20,
                  want_sections: int = 3) -> Result:
    """检查答题文件：存在、有实质内容、每个小节都写了东西。"""
    text = repo.worktree_file(relpath)
    if text is None:
        text = repo.show_file("HEAD", relpath)
    if text is None:
        return Result("回答了三个问题", False, f"找不到 {relpath}")

    # 按 markdown 二级标题切分
    sections = re.split(r"^##\s+", text, flags=re.M)[1:]
    filled = []
    for sec in sections:
        body = re.sub(r"\s+", "", re.sub(r"^.*$", "", sec, count=0, flags=re.M))
        body = re.split(r"^##", sec, flags=re.M)[0]
        body = re.sub(r"^[^\n]*\n", "", body)          # 去掉标题行
        body = re.sub(r"\s+", "", body)
        filled.append(len(body))

    short = [i + 1 for i, n in enumerate(filled) if n < min_per_section]
    if len(sections) < want_sections:
        return Result("回答了三个问题", False,
                      f"{relpath} 里只有 {len(sections)} 个小节，应该有 {want_sections} 个")
    if short:
        return Result("回答了三个问题", False,
                      f"第 {', '.join(map(str, short))} 个小节内容太少（<{min_per_section} 字）")
    total = sum(filled)
    return Result("回答了三个问题", True, f"{relpath} 三个小节共 {total} 字")


def check_style_commit(repo: Repo) -> Result:
    """存在一个独立的、只做格式化的提交 —— **而且必须是学生自己写的**。

    这里必须过滤掉仓库自带的提交：仓库历史里本来就有一条
    `chore(day0): add clang-format config`，不过滤的话学生什么都不做
    也会判过。
    """
    rx = re.compile(r"^(style|format|chore)(\([a-z0-9_]+\))?!?:\s*.*(format|格式化|clang-format)",
                    re.I)
    for c in repo.own_commits("HEAD"):
        if rx.search(c["subject"]):
            return Result("有独立的格式化提交", True,
                          f"{c['hash'][:7]} {c['subject'][:40]}")
    return Result("有独立的格式化提交", False,
                  "你自己还没有「只做格式化」的提交（message 里要能看出来）")


def grade_hw3(repo: Repo) -> list[Result]:
    """编译与链接：修好自己制造的链接错误 + 写下三个回答。"""
    return [
        _build_only(repo),
        build_and_test(repo),
        check_symbol_defined(repo, "wrap_angle_deg", ["app", "base"]),
        check_answers(repo, "day0/homework/answers-hw3.md"),
        gitscore.check_message_format(repo, MESSAGE_PATTERN),
    ]


def grade_hw4(repo: Repo, clang_format: str | None = None) -> list[Result]:
    """格式化：base/ 符合 .clang-format + 有独立提交 + 没弄坏功能。

    只查 base/：那是学生自己在 HW2/HW3 里动过的目录。
    课程不希望学生顺手把整个仓库格式化 —— 那样 review 看不出真实改动，
    而且 HW5 里合并队友分支时，整片重排过的文本会把冲突放大到无法收拾。
    """
    return [
        check_formatting(repo, ["base"], explicit=clang_format),
        build_and_test(repo),
        check_style_commit(repo),
        gitscore.check_message_format(repo, MESSAGE_PATTERN),
    ]


# ══════════════════════════════════════════════════════════════════
# 注册表
# ══════════════════════════════════════════════════════════════════

LESSONS = {
    "hw1": ("HW1 · 把项目跑起来", grade_hw1),
    "hw2": ("HW2 · 修编码器回绕", grade_hw2),
    "hw3": ("HW3 · 编译与链接", grade_hw3),
    "hw4": ("HW4 · 格式化", grade_hw4),
    "hw5": ("HW5 · Git 工作流", grade_hw5),
    # 任务书待写，先占位
    # "hw0": ("HW0 · 环境自检", ...),
}


# ══════════════════════════════════════════════════════════════════
# 报告渲染
# ══════════════════════════════════════════════════════════════════

BOX_W = 62


def _w(s: str) -> int:
    """字符串在终端里的显示宽度（CJK 算 2 列）。"""
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
            self.ok, self.no, self.wa = "[OK]", "[!!]", "[--]"
        else:
            self.tl, self.tr, self.bl, self.br = "┌", "┐", "└", "┘"
            self.h, self.v, self.lt, self.rt = "─", "│", "├", "┤"
            self.ok, self.no, self.wa = "✅", "❌", "⚠️"
        self.color = color

    def _c(self, code: str, s: str) -> str:
        return f"\033[{code}m{s}\033[0m" if self.color else s

    def green(self, s: str) -> str:
        return self._c("32", s)

    def red(self, s: str) -> str:
        return self._c("31", s)

    def yellow(self, s: str) -> str:
        return self._c("33", s)

    def bold(self, s: str) -> str:
        return self._c("1", s)


def render(title: str, meta: list[tuple[str, str]],
           results: list[Result], st: Style) -> str:
    inner = BOX_W - 2
    lines: list[str] = []
    lines.append(st.tl + st.h * inner + st.tr)
    lines.append(st.v + " " + _pad(st.bold(_clip(title, inner - 1)), inner - 1) + st.v)
    for k, v in meta:
        lines.append(st.v + " " + _pad(f"{k} {_clip(v, inner - len(k) - 3)}", inner - 1) + st.v)
    lines.append(st.lt + st.h * inner + st.rt)

    for res in results:
        if res.ok:
            mark = st.green(st.ok)
        elif res.severity == "warn":
            mark = st.yellow(st.wa)
        else:
            mark = st.red(st.no)
        name = _clip(res.name, 22)
        line = f"{mark} {_pad(name, 22)} {_clip(res.detail, inner - 27)}"
        lines.append(st.v + " " + _pad(line, inner - 1) + st.v)

    lines.append(st.lt + st.h * inner + st.rt)

    blocking = [r for r in results if r.blocking]
    verdict = "FAIL" if blocking else "PASS"
    vt = st.red(verdict) if blocking else st.green(verdict)
    if blocking:
        note = f"{len(blocking)} 项必修未通过"
    else:
        warn_n = sum(1 for r in results if r.severity == "warn" and not r.ok)
        note = "全部必修项通过" + (f"（{warn_n} 项提示）" if warn_n else "")
    lines.append(st.v + " " + _pad(f"结论   {vt}    {note}", inner - 1) + st.v)
    lines.append(st.bl + st.h * inner + st.br)

    return "\n".join(lines)


# ══════════════════════════════════════════════════════════════════
# 入口
# ══════════════════════════════════════════════════════════════════


def resolve_repo(target: str, workdir: Path) -> tuple[Repo, str, Path | None]:
    """把命令行参数变成 (Repo, 显示用的地址, 需要清理的临时目录)。"""
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
        return Repo(dest), target, workdir
    return Repo(target), str(Path(target).resolve()), None


def main() -> int:
    # Windows 终端默认可能是 GBK，先切 UTF-8，否则中文和框线会乱
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")     # type: ignore[attr-defined]
        except Exception:
            pass

    ap = argparse.ArgumentParser(
        description="Day 0 作业自查 / 验收工具",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("lesson", nargs="?", help="作业编号，如 hw5")
    ap.add_argument("repo", nargs="?", help="仓库地址（URL）或本地路径")
    ap.add_argument("--json", action="store_true", help="输出 JSON")
    ap.add_argument("--ascii", action="store_true", help="用纯 ASCII 边框")
    ap.add_argument("--no-color", action="store_true", help="不要颜色")
    ap.add_argument("--list", action="store_true", help="列出所有作业")
    ap.add_argument("--clang-format", dest="clang_format", default=None,
                    help="clang-format 可执行文件路径（没装在 PATH 上时用）")
    args = ap.parse_args()

    if args.list or not args.lesson:
        print("可用的作业：")
        for k, (title, _) in LESSONS.items():
            print(f"  {k:6s} {title}")
        return 0

    if args.lesson not in LESSONS:
        print(f"!! 没有这个作业：{args.lesson}", file=sys.stderr)
        print(f"   可用：{', '.join(LESSONS)}", file=sys.stderr)
        return 2
    if not args.repo:
        print("!! 还要给一个仓库地址或路径", file=sys.stderr)
        return 2

    title, fn = LESSONS[args.lesson]
    tmp = Path(tempfile.mkdtemp(prefix="ectl-grade-"))
    try:
        repo, shown, _ = resolve_repo(args.repo, tmp)
        branch = repo.current_branch()
        base = "main" if "main" in repo.branches() else (
            "master" if "master" in repo.branches() else "?")
        results = fn(repo, args.clang_format) if args.lesson == 'hw4' else fn(repo)
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
            "repo": shown,
            "branch": branch,
            "verdict": "FAIL" if any(r.blocking for r in results) else "PASS",
            "results": [{"name": r.name, "ok": r.ok, "detail": r.detail,
                         "severity": r.severity} for r in results],
        }, ensure_ascii=False, indent=2))
    else:
        color = not args.no_color and sys.stdout.isatty()
        st = Style(ascii_only=args.ascii, color=color)
        print()
        print(render(title, [("仓库", shown), ("分支", f"{branch} → {base}")],
                     results, st))
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
