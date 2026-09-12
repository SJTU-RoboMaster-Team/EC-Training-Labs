#!/usr/bin/env python3
"""配置 + 构建 + 跑测试。Windows / Linux / macOS 通用。

用法（在仓库根目录下）：

    python tools/build.py

只构建不跑测试：

    python tools/build.py --no-test

清理后重新构建：

    python tools/build.py --clean
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUILD_DIR = ROOT / "build"


def run(cmd: list[str]) -> int:
    """跑一条命令，实时打印输出，返回退出码。"""
    print("$ " + " ".join(str(c) for c in cmd))
    try:
        # 不要 capture_output：让学生实时看到编译器报错
        return subprocess.run([str(c) for c in cmd], cwd=str(ROOT)).returncode
    except FileNotFoundError:
        print(f"\n!! 找不到命令：{cmd[0]}")
        return 127


def guess_generators() -> list[str]:
    """按可用性排出一串候选生成器。

    **为什么需要这个**：Windows 上如果没装 Visual Studio，cmake 会默认挑
    "NMake Makefiles" —— 而 nmake 只在 VS 的开发者命令提示符里才有，
    普通终端里会报 `nmake: no such file or directory`，看起来像 cmake 坏了，
    其实只是选错了生成器。

    这里只挑**本机真的有**的生成器，所以不会凭空指定一个用不了的。
    """
    cands: list[str] = []
    if shutil.which("ninja"):
        cands.append("Ninja")
    if os.name == "nt":
        if shutil.which("mingw32-make"):
            cands.append("MinGW Makefiles")
        # 装了 VS 的话这个一定有
        vswhere = Path(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")) \
            / "Microsoft Visual Studio" / "Installer" / "vswhere.exe"
        if vswhere.exists():
            cands.append("Visual Studio 17 2022")
    else:
        if shutil.which("make"):
            cands.append("Unix Makefiles")
    return cands


def configure() -> int:
    """配置 CMake 工程。先用默认生成器，失败了再换一个能用的重试。"""
    base = ["cmake", "-S", ".", "-B", "build", "-DCMAKE_BUILD_TYPE=Debug"]

    # 已经有缓存就直接用（生成器不能再改，改了 cmake 会报错）
    if (ROOT / "build" / "CMakeCache.txt").exists():
        return run(base)

    # ① 先按 cmake 自己的默认来 —— 能跑通就别多事
    print("$ " + " ".join(base))
    first = subprocess.run([str(c) for c in base], cwd=str(ROOT),
                           capture_output=True, text=True, encoding="utf-8",
                           errors="replace")
    sys.stdout.write(first.stdout)
    sys.stderr.write(first.stderr)
    if first.returncode == 0:
        return 0

    # ② 默认失败：挑一个本机可用的生成器重试
    combined = (first.stdout + first.stderr).lower()
    looks_like_generator = any(
        s in combined for s in ("nmake", "no such file or directory",
                                "could not find", "generator", "cmake_cxx_compiler not set"))
    if not looks_like_generator:
        return first.returncode

    shutil.rmtree(ROOT / "build", ignore_errors=True)
    for gen in guess_generators():
        print()
        print(f"默认生成器不可用，改用 -G \"{gen}\" 重试 ……")
        cmd = base + ["-G", gen]
        print("$ " + " ".join(cmd))
        r = subprocess.run([str(c) for c in cmd], cwd=str(ROOT))
        if r.returncode == 0:
            return 0
        shutil.rmtree(ROOT / "build", ignore_errors=True)

    print()
    print("!! 试过的生成器都不行。请完成 Day 0 的环境配置，确认下面至少有一个可用：")
    print("     ninja / mingw32-make / make  （或者装 Visual Studio）")
    print("   用 CLion 的话：CLion 自带一套工具链，可以直接在 CLion 里构建。")
    return 1


def main() -> int:
    # 行缓冲：print 的内容会先进 Python 缓冲区，而子进程（cmake/g++）直接写 fd1，
    # 重定向到文件时顺序会错乱（"配置"标题跑到构建输出后面）。改成行缓冲即可。
    try:
        sys.stdout.reconfigure(line_buffering=True)     # type: ignore[attr-defined]
    except Exception:
        pass

    parser = argparse.ArgumentParser(description="构建并测试 day0/project")
    parser.add_argument("--no-test", action="store_true", help="只构建，不跑测试")
    parser.add_argument("--clean", action="store_true", help="先删掉 build/ 再构建")
    args = parser.parse_args()

    # 环境检查：先给出人话提示，而不是让 cmake 抛一堆看不懂的错
    if shutil.which("cmake") is None:
        print("!! 找不到 cmake。")
        print("   请先完成 Day 0 的环境配置，确认 `cmake --version` 有输出。")
        print("   用 CLion 的话：CLion 自带 cmake，在 Settings → Build → CMake 里能看到路径。")
        return 1
    # 编译器只做提示，不做硬性拦截 —— Windows 上用 CLion 自带的 MinGW 或 MSVC 时，
    # g++/clang++ 可能不在 PATH 上，但 cmake 自己能找到。真找不到时 cmake 会报得比我们清楚。
    if shutil.which("g++") is None and shutil.which("clang++") is None and shutil.which("cl") is None:
        print("提示：PATH 上没有找到 g++ / clang++ / cl，交给 cmake 自己找编译器。")
        print("      如果 cmake 报找不到编译器，见 Day 0 课件的环境配置一节。")
        print()

    if args.clean and BUILD_DIR.exists():
        print(f"删除 {BUILD_DIR}")
        shutil.rmtree(BUILD_DIR)

    print("=" * 60)
    print("配置 (cmake configure)")
    print("=" * 60)
    rc = configure()
    if rc != 0:
        return rc

    print()
    print("=" * 60)
    print("构建 (cmake build)")
    print("=" * 60)
    rc = run(["cmake", "--build", "build", "--config", "Debug"])
    if rc != 0:
        return rc

    if args.no_test:
        return 0

    print()
    print("=" * 60)
    print("测试 (ctest)")
    print("=" * 60)
    # 注意返回码：**构建成功就算成功**。
    # HW1 阶段 test_encoder 本来就该挂一个用例，那是正常的，
    # 不能让 ctest 的失败码把学生吓一跳。
    rc = run(["ctest", "--test-dir", "build", "--output-on-failure", "-C", "Debug"])
    print()
    if rc == 0:
        print("全部测试通过。")
    else:
        print("构建成功；上面有测试没通过 —— 这在 HW1 阶段是预期的（HW2 会修）。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
