#!/usr/bin/env python3
"""courses.day0_git —— Day 0 工程协作（Git）模块的全部课程知识。

**换一门课，只需要写这样一个文件。** 引擎（`grade.py`）和规则库（`rulelib/`）
里没有任何一句「HW5」「CALIBRATE」「day0/project」。

这个文件里有三样东西：

  1. 这门课的约定（工程在哪、commit message 长什么样、哪些词算废话）
  2. 只有这门课才有的规则（那三个 TODO、那个格式化提交）
  3. `LESSONS`：每份作业 = 一串规则调用

规则函数保持 `f(repo, ...) -> Result` 的普通签名，用 `R()` 把参数绑上即可。
"""

from __future__ import annotations

import re

from rulelib import code, git
from rulelib.base import R, Repo, Result

# ══════════════════════════════════════════════════════════════════
# 这门课的约定
# ══════════════════════════════════════════════════════════════════

MODULE = "day0-git"
MODULE_TITLE = "Day 0 · 工程协作"

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
    f"{PROJECT}/build/app.o",
    f"{PROJECT}/build/CMakeCache.txt",
    f"{PROJECT}/mcu/stm32f407/MDK-ARM/DebugConfig/day0.dbgconf",
    f"{PROJECT}/mcu/stm32f407/MDK-ARM/RTE/_day0/RTE_Components.h",
    f"{PROJECT}/mcu/stm32f407/MDK-ARM/day0.uvguix.zhangsan",
]


# ══════════════════════════════════════════════════════════════════
# 只有这门课才有的规则
# ══════════════════════════════════════════════════════════════════


def _merged(repo: Repo, rel: str) -> str:
    """工作区优先，其次 HEAD —— 学生自查时改动可能还没提交。"""
    return repo.worktree_file(rel) or repo.show_file("HEAD", rel) or ""


def check_todos_done(repo: Repo) -> Result:
    """HW5 的三个 TODO 是否都真的处理了。

    这是**题目本身**，所以它属于课程，不属于规则库。

    只查「结果对不对」，不查写法 —— 例如 `kDefaultClampSpeed` 只要是 6.0
    （4.0 的 1.5 倍），怎么写都行。
    """
    problems: list[str] = []

    # TODO-a：夹爪速度调到 6.0（4.0 × 1.5）
    ctl = _merged(repo, f"{PROJECT}/app/control.cpp")
    m = re.search(r"kDefaultClampSpeed\s*=\s*([0-9.]+)f", ctl)
    if not m:
        problems.append("control.cpp 里找不到 kDefaultClampSpeed")
    elif abs(float(m.group(1)) - 6.0) > 0.01:
        problems.append(f"夹爪速度还是 {m.group(1)}，TODO-a 要求按 1.5 倍调到 6.0")

    # TODO-b：标定期间跳过阻力判断
    clp = _merged(repo, f"{PROJECT}/app/clamp.cpp")
    if "is_calibrating_" not in clp.split("ClampState Clamp::update", 1)[-1]:
        problems.append("clamp.cpp 的 update() 里没有用 is_calibrating_ 跳过阻力判断")

    # TODO-c：CALIBRATE（这条由"冲突保留双方意图"覆盖，这里只确认它还在）
    arm = _merged(repo, f"{PROJECT}/app/arm.h")
    if "CALIBRATE" not in arm:
        problems.append("arm.h 里没有 CALIBRATE")

    if problems:
        return Result("三个 TODO 都已处理", False, "；".join(problems[:2]))
    return Result("三个 TODO 都已处理", True, "夹爪速度 / 标定判断 / 工作模式 都改了")


def check_style_commit(repo: Repo) -> Result:
    """存在一个独立的、只做格式化的提交 —— **而且必须是学生自己写的**。

    这里必须过滤掉仓库自带的提交：仓库历史里本来就有一条
    `chore(day0): add clang-format config`，不过滤的话学生什么都不做
    也会判过。（这个坑是 verify_chain 抓出来的。）
    """
    rx = re.compile(r"^(style|format|chore)(\([a-z0-9_]+\))?!?:\s*.*(format|格式化|clang-format)",
                    re.I)
    for c in repo.own_commits("HEAD"):
        if rx.search(c["subject"]):
            return Result("有独立的格式化提交", True,
                          f"{c['hash'][:7]} {c['subject'][:40]}")
    return Result("有独立的格式化提交", False,
                  "你自己还没有「只做格式化」的提交（message 里要能看出来）")


# ══════════════════════════════════════════════════════════════════
# 作业定义
#
# 每条规则和任务书「评分」一节的必修项**一一对应**，
# 数量对不上会被 verify_chain.py 当场抓住。
# ══════════════════════════════════════════════════════════════════

LESSONS: dict[str, tuple[str, list]] = {
    "hw1": ("HW1 · 把项目跑起来", [
        R(code.check_build, PROJECT),
        R(git.check_worktree_clean),                       # 提示
    ]),

    "hw2": ("HW2 · 修编码器回绕", [
        R(code.check_tests, PROJECT),
        R(git.check_path_unmodified, f"{PROJECT}/tests"),
        R(git.check_message_format, MESSAGE_PATTERN),
    ]),

    "hw3": ("HW3 · 编译与链接", [
        R(code.check_build, PROJECT),
        R(code.check_tests, PROJECT),
        R(code.check_symbol_defined, PROJECT, "wrap_angle_deg", ["app", "base"]),
        R(code.check_answers, "day0/homework/answers-hw3.md"),
        R(git.check_message_format, MESSAGE_PATTERN),
    ]),

    "hw4": ("HW4 · 格式化", [
        R(code.check_formatting, PROJECT, ["base"]),
        R(code.check_tests, PROJECT),
        R(check_style_commit),
        R(git.check_message_format, MESSAGE_PATTERN),
    ]),

    "hw5": ("HW5 · Git 工作流", [
        # ── 必修（与任务书「评分」一节一一对应）──
        R(git.check_branch_naming, BRANCH_PATTERN),
        R(git.check_branch_has_work, BRANCH_PATTERN),
        R(git.check_message_format, MESSAGE_PATTERN),
        R(git.check_message_blacklist, BLACKLIST),
        R(git.check_no_artifacts),
        R(git.check_no_conflict_markers, paths=[PROJECT]),
        R(git.check_path_unmodified, f"{PROJECT}/tests"),
        R(git.check_file_contains, f"{PROJECT}/app/arm.h", ["CALIBRATE", "DROP_MODE"],
          name="冲突保留双方意图"),
        check_todos_done,
        R(git.check_merge_happened),
        R(code.check_tests, PROJECT),
        # ── 提示（只显示，不影响结论）──
        R(git.check_commit_count, 15),
        R(git.check_message_length, lo=10, hi=72),
        R(git.check_atomic_heuristic, max_top_dirs=3),
        R(git.check_worktree_clean),
        R(git.check_pushed),
    ]),
}
