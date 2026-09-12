#!/usr/bin/env python3
"""rulelib.code —— 与课程无关的 C/C++ 检查规则。

规则函数一律 `check_` 开头，签名是 `check_xxx(repo, project, ...) -> Result`；
纯工具函数（找编译器之类）不加前缀。

这里的规则不认识「HW5」「cpp1」——工程在哪、要查什么，都由 `courses/` 传进来。

**四类手段：**

  build / tests      真的把它编译出来、跑起来（最贵，也最可信）
  contract / symbol  把一小段探针 .cpp 和学生仓库的头文件一起编译
                     —— 报错信息就是 C++ 编译器自己说的话
  formatting         风格（有 clang-format 就精确查，没有就退回缩进启发式）
  no_token           源码规则（先剥注释和字符串，避免误报）

探针（contract / symbol）不跑 cmake、不依赖学生的构建系统，
一条 g++ 命令就够 —— 快，而且不会被「学生把 CMakeLists 改坏了」干扰。
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from .base import Repo, Result

# ══════════════════════════════════════════════════════════════════
# 工具
# ══════════════════════════════════════════════════════════════════


def find_tool(name: str) -> str | None:
    return shutil.which(name)


def find_clang_format(explicit: str | None = None) -> str | None:
    """找一个能用的 clang-format。

    **大多数人不会单独装 clang-format，但 CLion 自带一个**，
    所以除了 PATH 还要去 CLion / JetBrains Toolbox 的安装目录里翻。

    实在找不到也没关系 —— check_formatting 会退回到缩进启发式。
    """
    explicit = explicit or os.environ.get("CLANG_FORMAT")
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


def find_cxx() -> str | None:
    """找一个 C++ 编译器，给探针用（不依赖学生的构建系统）。"""
    for name in ("g++", "clang++", "c++"):
        exe = shutil.which(name)
        if exe:
            return exe
    return None


def _sources(root: Path, subdirs: list[str] | None = None) -> list[Path]:
    """收集 .cpp / .h（可选限定子目录）。"""
    bases = [root / d for d in subdirs] if subdirs else [root]
    out: list[Path] = []
    for base in bases:
        if base.is_dir():
            out += sorted(base.rglob("*.cpp")) + sorted(base.rglob("*.h"))
    return out


def _run(cmd: list[str], cwd: Path | None = None, timeout: int = 300):
    return subprocess.run(cmd, cwd=str(cwd) if cwd else None,
                          capture_output=True, text=True, encoding="utf-8",
                          errors="replace", timeout=timeout)


# ══════════════════════════════════════════════════════════════════
# 构建与测试
# ══════════════════════════════════════════════════════════════════


def _shorten(text: str, prefixes: list[str]) -> str:
    """把绝对路径砍成相对路径 —— 报错里那一长串 `/home/xxx/.../day0/cpp/`
    对学生的判断没有任何帮助，只会把真正有用的部分挤出屏幕。"""
    for pfx in prefixes:
        if pfx:
            text = text.replace(pfx.rstrip("/") + "/", "")
            text = text.replace(pfx.rstrip("/"), "")
    return text


def _best_error_lines(text: str, n: int = 2, prefixes: list[str] | None = None) -> str:
    """从构建输出里挑出最该给学生看的那几行。

    直接取末尾几行会拿到 `gmake[1]: *** Waiting for unfinished jobs....` 这种噪声，
    学生看了不知道改哪。优先取编译器自己的诊断（含 `error:`），
    退而求其次取含 error / Error 的行，最后才用末尾几行。
    """
    text = _shorten(text or "", prefixes or [])
    lines = [l.rstrip() for l in text.splitlines() if l.strip()]
    if not lines:
        return "（没有任何输出）"
    # 顺序有讲究：`undefined reference` 最可操作，`collect2: error:` 最没用
    for key in ("undefined reference", "fatal error:", "error:"):
        hits = [l for l in lines if key in l]
        if hits:
            return " / ".join(h.strip()[:110] for h in hits[:n])
    hits = [l for l in lines if "rror" in l]
    if hits:
        return " / ".join(h.strip()[:110] for h in hits[-n:])
    return " / ".join(l.strip()[:110] for l in lines[-n:])


def check_build(repo: Repo, project: str) -> Result:
    """能在**全新的临时目录**里配置并编译通过。

    为什么不用学生自己的 `build/`：那是增量目录，上一次的 .o 还在；
    构建失败时测试二进制仍是旧的，跑出来的「全绿」是假的。
    """
    proj = repo.root / project
    if not (proj / "CMakeLists.txt").is_file():
        return Result("能构建", False, f"找不到 {project}/CMakeLists.txt")
    if not find_tool("cmake"):
        return Result("能构建", False, "本机找不到 cmake，无法验证")

    with tempfile.TemporaryDirectory(prefix="ectl-grade-") as td:
        cfg = _run(["cmake", "-S", str(proj), "-B", td])
        if cfg.returncode != 0:
            return Result("能构建", False, "cmake 配置失败："
                          + _best_error_lines(cfg.stderr or cfg.stdout, prefixes=[td, str(proj)]))
        bld = _run(["cmake", "--build", td, "-j"])
        if bld.returncode != 0:
            return Result("能构建", False, "编译失败："
                          + _best_error_lines(bld.stdout + bld.stderr, prefixes=[td, str(proj)]))
    return Result("能构建", True, "cmake 配置 + 编译通过")


def check_tests(repo: Repo, project: str, want: list[str] | None = None,
                title: str = "测试全部通过") -> Result:
    """在新临时目录里构建并跑测试，要求全部用例通过。

    want: 要求必须通过的测试名；None 表示"找到几个就查几个"
    title: 显示名。一节课里查两次测试时（比如"新的要过 + 旧的没被改坏"）
           必须给不同的名字，否则输出里两行长得一样，学生分不清哪行是哪行。
           （注意别把这个参数叫 `name` —— 下面 `for name in want` 会把它冲掉。）
    """
    proj = repo.root / project
    if not (proj / "CMakeLists.txt").is_file():
        return Result(title, False, f"找不到 {project}/CMakeLists.txt")
    if not find_tool("cmake"):
        return Result(title, False, "本机找不到 cmake，无法验证")

    with tempfile.TemporaryDirectory(prefix="ectl-grade-") as td:
        cfg = _run(["cmake", "-S", str(proj), "-B", td])
        if cfg.returncode != 0:
            return Result(title, False, "cmake 配置失败："
                          + _best_error_lines(cfg.stderr or cfg.stdout, prefixes=[td, str(proj)]))

        bld = _run(["cmake", "--build", td, "-j"])
        if bld.returncode != 0:
            return Result(title, False, "编译失败："
                          + _best_error_lines(bld.stdout + bld.stderr, prefixes=[td, str(proj)]))

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
            name = exe.stem
            if not name.startswith("test_"):
                continue
            if exe.suffix and exe.suffix.lower() not in (".exe", ""):
                continue
            if os.name != "nt" and not os.access(exe, os.X_OK):
                continue
            try:
                r = subprocess.run([str(exe)], capture_output=True, text=True,
                                   encoding="utf-8", errors="replace", timeout=60)
            except (OSError, subprocess.TimeoutExpired):
                continue
            results[name] = r.stdout

    if not results:
        return Result(title, False, "没有找到任何测试可执行文件")

    if want is None:
        want = sorted(results)

    summary, failed = [], []
    for name in want:
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
        return Result(title, False, "；".join(failed))
    return Result(title, True, " · ".join(summary))


# ══════════════════════════════════════════════════════════════════
# 探针：把一小段 .cpp 和学生的头文件一起编译
# ══════════════════════════════════════════════════════════════════


def _probe(repo: Repo, project: str, probe: Path, mode: str,
           extra: list[str] | None = None) -> tuple[int, str]:
    """编译一个探针。返回 (返回码, 诊断文本)。

    `-I<project>` 让探针能 include 学生的头文件；探针本身在课程目录里，
    **不往学生仓库写任何东西**。
    """
    cxx = find_cxx()
    if not cxx:
        return 127, "本机找不到 C++ 编译器（g++ / clang++）"
    cmd = [cxx, f"-I{repo.root / project}", "-Wall", *(extra or [])]
    cmd += [str(probe)] if mode == "syntax" else ["-c", str(probe), "-o", os.devnull]
    if mode == "syntax":
        cmd.insert(1, "-fsyntax-only")
    r = _run(cmd, cwd=probe.parent)
    return r.returncode, (r.stderr or r.stdout)


def _first_static_assert(log: str) -> str | None:
    """从编译输出里挑出 static_assert 的那句人话。

    探针里写的是 `static_assert(条件, "说明")`，编译器的报错长这样：
        error: static assertion failed: 说明
    我们要的就是那个「说明」—— 它是写给学生的。
    """
    m = re.search(r"static assertion failed[:\s]*(.*)", log)
    if m and m.group(1).strip():
        return m.group(1).strip()
    return None


def check_contract(repo: Repo, project: str, probe: Path,
                   why: str = "") -> Result:
    """契约检查：探针里的 `static_assert` 必须全部成立。

    报错信息就是 C++ 编译器自己说的话 —— **验收工具本身成了教学内容**：
    学生被 static_assert 拦一次，就顺便学会了读编译器的诊断。
    """
    name = why or probe.stem.replace("_", " ")
    if not probe.is_file():
        return Result(name, False, f"探针文件不存在：{probe}")
    rc, log = _probe(repo, project, probe, "syntax")
    if rc == 127:
        return Result(name, False, log)
    if rc == 0:
        return Result(name, True, "契约成立（探针编译通过）")
    msg = _first_static_assert(log)
    if msg:
        return Result(name, False, msg)
    tail = [l for l in log.strip().splitlines() if "error" in l][:1]
    return Result(name, False, (tail[0].strip()[:110] if tail else "探针编译失败"))


# 符号表里每个字母是什么意思（`nm` 的输出）
SYMBOL_KINDS = {
    "T": "全局定义（普通函数）",
    "t": "文件内定义（static / 匿名命名空间）",
    "W": "弱符号（inline / 模板实例化）",
    "w": "弱符号（static inline）",
    "U": "未定义（只有声明，等链接器去找）",
    "V": "弱对象（inline 变量）",
    "B": "未初始化全局（.bss）",
    "D": "已初始化全局（.data）",
}


def check_symbol_kind(repo: Repo, project: str, probe: Path, symbol: str,
                      kind: str) -> Result:
    """`symbol` 在探针的目标文件里必须是 `kind` 这类符号。

    用途：验证「头文件里的函数确实被当成 inline 处理了」（应该是 `W`）、
    「这个函数是文件内私有的」（应该是 `t`）、
    「这里只有声明没有定义」（应该是 `U`）——
    这些是读代码看不出来、只有符号表会说的东西。
    """
    if not probe.is_file():
        return Result(f"{symbol} 是 {kind} 类符号", False, f"探针不存在：{probe}")
    nm = find_tool("nm")
    if not nm:
        return Result(f"{symbol} 是 {kind} 类符号", False, "本机找不到 nm")

    with tempfile.TemporaryDirectory(prefix="ectl-nm-") as td:
        obj = Path(td) / "probe.o"
        cxx = find_cxx()
        if not cxx:
            return Result(f"{symbol} 是 {kind} 类符号", False, "本机找不到 C++ 编译器")
        r = _run([cxx, f"-I{repo.root / project}", "-c", str(probe), "-o", str(obj)],
                 cwd=probe.parent)
        if r.returncode != 0:
            tail = [l for l in (r.stderr or "").strip().splitlines() if "error" in l][:1]
            return Result(f"{symbol} 是 {kind} 类符号", False,
                          "探针编译失败：" + (tail[0].strip()[:90] if tail else "?"))
        out = _run([nm, "-C", str(obj)]).stdout

    hit = None
    for line in out.splitlines():
        parts = line.split()
        if len(parts) >= 2 and parts[-1].split("(")[0].strip() == symbol:
            hit = parts[-2] if len(parts) >= 3 else parts[0]
            break
    if hit is None:
        return Result(f"{symbol} 是 {kind} 类符号", False,
                      f"符号表里找不到 {symbol}")
    if hit != kind:
        return Result(f"{symbol} 是 {kind} 类符号", False,
                      f"实际是 {hit}（{SYMBOL_KINDS.get(hit, '?')}），"
                      f"期望 {kind}（{SYMBOL_KINDS.get(kind, '?')}）")
    return Result(f"{symbol} 是 {kind} 类符号", True,
                  f"{hit} = {SYMBOL_KINDS.get(kind, '')}")


# ══════════════════════════════════════════════════════════════════
# 风格
# ══════════════════════════════════════════════════════════════════


def _indent_width(project: Path) -> int:
    """工程 .clang-format 里的缩进宽度。用来在没装 clang-format 时做粗略判断。"""
    f = project / ".clang-format"
    if f.is_file():
        m = re.search(r"^IndentWidth:\s*(\d+)", f.read_text(encoding="utf-8"), re.M)
        if m:
            return int(m.group(1))
    return 2      # LLVM 默认


def _indent_heuristic(root: Path, subdirs: list[str], width: int) -> tuple[int, int]:
    """数一数「缩进不是 width 整数倍」的行有多少。

    实测（4 空格配置）：未格式化 88.9%，已格式化 0.0% —— 区分度足够大。
    **这是启发式，不是精确判断**，只在没有 clang-format 时兜底。
    """
    bad = tot = 0
    for f in _sources(root, subdirs):
        if f.suffix != ".h" and f.suffix != ".cpp":
            continue
        for line in f.read_text(encoding="utf-8", errors="replace").splitlines():
            m = re.match(r"^( +)\S", line)
            if not m:
                continue
            tot += 1
            if len(m.group(1)) % width != 0:
                bad += 1
    return bad, tot


def check_formatting(repo: Repo, project: str, subdirs: list[str],
                     explicit: str | None = None) -> Result:
    """这些目录下的 C++ 文件是否符合工程的 .clang-format。

    两条路：
      ① 有 clang-format（PATH 上或 CLion 自带的）→ 精确检查
      ② 没有 → 退回到缩进启发式（会在结果里标明）
    """
    proj = repo.root / project
    files = [f for f in _sources(proj, subdirs)]
    if not files:
        return Result("代码符合 clang-format", False, f"在 {subdirs} 下没找到 C++ 文件")

    exe = find_clang_format(explicit)
    if exe:
        bad: list[str] = []
        for f in files:
            r = _run([exe, "--style=file", "--dry-run", "--Werror", str(f)],
                     cwd=proj, timeout=60)
            if r.returncode != 0:
                bad.append(f.relative_to(proj).as_posix())
        if bad:
            return Result("代码符合 clang-format", False,
                          f"{len(bad)}/{len(files)} 个文件需要重排：{', '.join(bad[:3])}")
        return Result("代码符合 clang-format", True,
                      f"{len(files)}/{len(files)} 个文件合规（clang-format 精确检查）")

    width = _indent_width(proj)
    bad, tot = _indent_heuristic(proj, subdirs, width)
    pct = (100.0 * bad / tot) if tot else 0.0
    if pct > 20.0:
        return Result("代码符合 clang-format", False,
                      f"约 {pct:.0f}% 的缩进行不是 {width} 空格的整数倍 —— 看起来没格式化过")
    return Result("代码符合 clang-format", True,
                  f"缩进看起来符合（{width} 空格；本机没有 clang-format，用启发式判断）")


# ══════════════════════════════════════════════════════════════════
# 源码规则
# ══════════════════════════════════════════════════════════════════


def strip_comments_and_strings(text: str) -> str:
    """把注释和字符串字面量换成等长空白。

    为什么要剥：`// 这里不能用 double` 这种注释不该触发「不许出现 double」，
    `"double"` 这种字符串同理。**换等长空白而不是删掉**，
    这样行号和列号不会漂。
    """
    out = []
    i, n = 0, len(text)
    while i < n:
        c = text[i]
        if c == "/" and i + 1 < n and text[i + 1] == "/":
            j = text.find("\n", i)
            j = n if j < 0 else j
            out.append(" " * (j - i))
            i = j
        elif c == "/" and i + 1 < n and text[i + 1] == "*":
            j = text.find("*/", i + 2)
            j = n if j < 0 else j + 2
            out.append("".join(ch if ch == "\n" else " " for ch in text[i:j]))
            i = j
        elif c in "\"'":
            j = i + 1
            while j < n and text[j] != c:
                j += 2 if text[j] == "\\" else 1
            j = min(j + 1, n)
            out.append("".join(ch if ch == "\n" else " " for ch in text[i:j]))
            i = j
        else:
            out.append(c)
            i += 1
    return "".join(out)


def check_no_token(repo: Repo, project: str, tokens: list[str],
                   why: str = "", subdirs: list[str] | None = None) -> Result:
    """这些标识符不许出现在源码里（注释和字符串不算）。

    用途举例：两个固件工程都只开单精度 FPU（`-mfpu=…-sp-d16`），
    `double` 一次都不该出现 —— 它是软件模拟，一次除法几十条指令。
    """
    root = repo.root / project
    hits: list[str] = []
    for f in _sources(root, subdirs):
        text = strip_comments_and_strings(f.read_text(encoding="utf-8", errors="replace"))
        for t in tokens:
            # 同一行出现两次不算两条 —— 学生要看的是"去哪一行改"
            lines = sorted({text[:m.start()].count("\n") + 1
                            for m in re.finditer(rf"\b{re.escape(t)}\b", text)})
            hits += [f"{f.relative_to(root).as_posix()}:{n} 出现 {t}" for n in lines]
    name = f"不出现 {'/'.join(tokens)}"
    if hits:
        detail = "；".join(hits[:3]) + (f"（共 {len(hits)} 处）" if len(hits) > 3 else "")
        return Result(name, False, detail + (f" —— {why}" if why else ""))
    return Result(name, True, why or f"{len(tokens)} 个标识符都没出现")


# ══════════════════════════════════════════════════════════════════
# 文档类（作业里的「回答问题」）
# ══════════════════════════════════════════════════════════════════


def check_answers(repo: Repo, relpath: str, min_per_section: int = 20,
                  want_sections: int = 3) -> Result:
    """检查答题文件：存在、有实质内容、每个小节都写了东西。

    纯自动验只能验「构建过了」，验不了「他懂没懂」。
    让他写几句话 + 查每节字数，是低成本的「至少读了一遍」。
    **这不是防作弊**，是保证他不是空着交。
    """
    name = f"回答了{want_sections}个问题"
    text = repo.worktree_file(relpath)
    if text is None:
        text = repo.show_file("HEAD", relpath)
    if text is None:
        return Result(name, False, f"找不到 {relpath}")

    sections = re.split(r"^##\s+", text, flags=re.M)[1:]
    filled = []
    for sec in sections:
        body = re.split(r"^##", sec, flags=re.M)[0]
        body = re.sub(r"^[^\n]*\n", "", body)          # 去掉标题行
        body = re.sub(r"\s+", "", body)
        filled.append(len(body))

    if len(sections) < want_sections:
        return Result(name, False,
                      f"{relpath} 里只有 {len(sections)} 个小节，应该有 {want_sections} 个")
    short = [i + 1 for i, n in enumerate(filled) if n < min_per_section]
    if short:
        return Result(name, False,
                      f"第 {', '.join(map(str, short))} 个小节内容太少（<{min_per_section} 字）")
    return Result(name, True, f"{relpath} {want_sections} 个小节共 {sum(filled)} 字")


def check_symbols_defined(repo: Repo, project: str, symbols: list[str],
                          subdirs: list[str]) -> Result:
    """一批函数是不是**都有定义**。返回一条结果，列出缺哪几个。

    比逐个查更好用：学生一次看到"还差哪几个"，而且规则名可读
    （逐个查的话，跳过时只能显示函数名 `check_symbol_defined` ×4，看不出区别）。
    """
    missing = []
    for sym in symbols:
        if not check_symbol_defined(repo, project, sym, subdirs).ok:
            missing.append(sym)
    name = f"{len(symbols)} 个函数都有实现"
    if missing:
        return Result(name, False,
                      f"还差 {len(missing)} 个没实现：{', '.join(missing)}"
                      "（只有声明、没有定义 → undefined reference）")
    return Result(name, True, f"{', '.join(symbols)} 都在")


def check_symbol_defined(repo: Repo, project: str, symbol: str,
                         subdirs: list[str]) -> Result:
    """某个函数**有定义**（不是只有声明）。

    纯文本判断，不建工程 —— 这一条查的是「学生有没有意识到
    『改了头文件还得有地方实现它』」，用正则足够。
    要更硬的证据用 `check_symbol_kind`。
    """
    root = repo.root / project
    pat = re.compile(rf"\b{re.escape(symbol)}\s*\([^;{{]*\)\s*(?:const\s*)?\{{")
    for f in _sources(root, subdirs):
        try:
            text = f.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if pat.search(strip_comments_and_strings(text)):
            return Result(f"{symbol} 有实现", True,
                          f"在 {f.relative_to(root).as_posix()} 里找到定义")
    return Result(f"{symbol} 有实现", False,
                  "只找到声明，没找到实现（这会导致 undefined reference）")
