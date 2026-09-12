#!/usr/bin/env python3
"""courses.cpp_basics —— C++ 基础模块的全部课程知识。

**这是「换一门课只写一个文件」的第二个例子**（第一个是 `day0_git.py`）。
引擎和规则库一行都不用改。

模块设计见 `CppBasics/SYLLABUS.md`：知识点是从两个真实仓库
（Wheel-Legged-Robot-2026 / RM2026-Dual-Arm-Engineer, 389 文件 70822 行）
统计出来的，练习工程 `day0/cpp/` 是它们的抽象版。

与 HW1–HW5 **完全独立**：编号 `cpp1…cppN`，共用同一套 graderr 和同一套自查习惯。
"""

from __future__ import annotations

from pathlib import Path

from rulelib import code, git
from rulelib.base import R

MODULE = "cpp-basics"
MODULE_TITLE = "C++ 基础 · 自学模块"

PROJECT = "day0/cpp"
PROBES = Path(__file__).resolve().parent / "probes"

MESSAGE_PATTERN = r"^(feat|fix|refactor|docs|test|chore|tune|style)(\([a-z0-9_]+\))?!?: .+"


# ══════════════════════════════════════════════════════════════════
# 作业定义
#
# 这些课是**有先后顺序**的（cpp1 不过，后面的契约根本编不过），
# 所以都开了 stop_on_fail：第一条必修项没过就停，剩下的记成「跳过」。
# 默认是关的 —— Git 那类互相独立的检查要全部跑完，让学生一次看到所有问题。
# ══════════════════════════════════════════════════════════════════

LESSONS: dict[str, tuple] = {
    # ── cpp1 · 声明与定义 ──────────────────────────────────────
    # math.cpp 是空的 → 链接报 undefined reference（HW3 那个概念的复现）
    "cpp1": ("C++01 · 声明与定义", [
        R(code.check_build, PROJECT, _label="能编译"),
        R(code.check_tests, PROJECT, ["test_math"], _label="test_math 全过"),
        R(code.check_symbols_defined, PROJECT,
          ["limit", "loopLimit", "degNormalize180", "isNanOrInf"], ["base"],
          _label="四个函数都有定义"),
        R(code.check_contract, PROJECT, PROBES / "param_const_ref.cpp",
          _label="函数签名没改"),
        R(git.check_message_format, MESSAGE_PATTERN, _label="commit message 格式"),
    ], {"stop_on_fail": True}),

    # ── cpp2 · 函数与参数传递 ──────────────────────────────────
    # 重点：限幅与类型转换的先后顺序（先转再限幅，超大值行为不可预期）
    "cpp2": ("C++02 · 函数与参数传递", [
        R(code.check_build, PROJECT, _label="能编译"),
        R(code.check_tests, PROJECT, ["test_motor"], _label="test_motor 全过"),
        R(code.check_contract, PROJECT, PROBES / "torque_signature.cpp",
          _label="setTorque 签名没改"),
        R(git.check_message_format, MESSAGE_PATTERN, _label="commit message 格式"),
    ], {"stop_on_fail": True}),

    # ── cpp3 · 枚举、switch 与指针数组 ─────────────────────────
    # 依赖 cpp2：Chassis::update 要调 Motor::setTorque
    "cpp3": ("C++03 · 枚举、switch 与指针", [
        R(code.check_build, PROJECT, _label="能编译"),
        R(code.check_tests, PROJECT, ["test_chassis"], _label="test_chassis 全过"),
        R(code.check_tests, PROJECT, ["test_motor"], _label="test_motor 没被改坏"),
        R(git.check_message_format, MESSAGE_PATTERN, _label="commit message 格式"),
    ], {"stop_on_fail": True}),

    # ── cpp4 · 位运算与结构体布局（CAN 前置）────────────────────
    "cpp4": ("C++04 · 位运算与 CAN 打包", [
        R(code.check_build, PROJECT, _label="能编译"),
        R(code.check_tests, PROJECT, ["test_can"], _label="test_can 全过"),
        # 两个工程都只开单精度 FPU，double 一次都不该出现
        R(code.check_no_token, PROJECT, ["double"],
          why="两个工程都是单精度 FPU（-mfpu=…-sp-d16），double 是软件模拟",
          _label="不许出现 double"),
        R(code.check_contract, PROJECT, PROBES / "float_only.cpp",
          _label="浮点返回 float"),
        R(git.check_message_format, MESSAGE_PATTERN, _label="commit message 格式"),
    ], {"stop_on_fail": True}),
}
