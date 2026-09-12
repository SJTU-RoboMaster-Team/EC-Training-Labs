#!/usr/bin/env python3
"""rulelib.git —— 与课程无关的 Git 规则库。

规则都是普通函数：输入 `Repo`，输出 `Result`。
这个文件不认识「Day 0」「HW5」「cpp1」——那些在 `courses/` 里。

加一门 Git 相关的新课，不需要动这个文件。
"""

from __future__ import annotations

import fnmatch
import re

from .base import Repo, Result

# ══════════════════════════════════════════════════════════════════
# 通用规则
# ══════════════════════════════════════════════════════════════════

# 构建产物 / 生成文件的路径特征。这些**永远不该**进版本库。
ARTIFACT_PATTERNS = [
    "build/*", "*/build/*", "Build/*", "*/Build/*",
    "Debug/*", "Release/*",
    "*.o", "*.obj", "*.elf", "*.hex", "*.bin", "*.map", "*.axf",
    "*.d", "*.crf", "*.dep", "*.lnp", "*.sct", "*.iex", "*.lst", "*.htm",
    "*DebugConfig*", "*/RTE/*", "*uvguix*",
    ".cache/*", "*/.cache/*",
    "*.pyc", "__pycache__/*",
]


def check_message_format(repo: Repo, pattern: str, rev: str = "HEAD",
                         skip_merges: bool = True) -> Result:
    """所有 commit message 必须匹配 pattern。"""
    rx = re.compile(pattern)
    commits = repo.commits(rev)
    bad = [c for c in commits
           if not (skip_merges and len(c["parents"]) >= 2)
           and not rx.match(c["subject"])]
    total = sum(1 for c in commits if not (skip_merges and len(c["parents"]) >= 2))
    if bad:
        detail = "；".join(f"{c['hash'][:7]} {c['subject'][:32]!r}" for c in bad[:3])
        if len(bad) > 3:
            detail += f" …等 {len(bad)} 条"
        return Result("message 格式", False, f"{len(bad)}/{total} 条不合规：{detail}")
    return Result("message 格式", True, f"{total}/{total} 条合规")


def check_message_blacklist(repo: Repo, words: list[str], rev: str = "HEAD") -> Result:
    """commit subject 不得是低信息量的词。"""
    commits = repo.commits(rev)
    hits = []
    for c in commits:
        if len(c["parents"]) >= 2:      # merge commit 的默认 message 不算
            continue
        core = re.sub(r"^[A-Za-z]+(\([^)]*\))?!?:\s*", "", c["subject"]).strip().lower()
        if core in {w.lower() for w in words} or c["subject"].strip().lower() in {w.lower() for w in words}:
            hits.append(c)
    if hits:
        detail = "；".join(f"{c['hash'][:7]} {c['subject'][:24]!r}" for c in hits[:3])
        return Result("message 黑名单", False, f"{len(hits)} 条低信息量：{detail}")
    return Result("message 黑名单", True, "没有低信息量 message")


def check_message_length(repo: Repo, lo: int = 10, hi: int = 72,
                         rev: str = "HEAD", severity: str = "warn") -> Result:
    commits = [c for c in repo.commits(rev) if len(c["parents"]) < 2]
    bad = [c for c in commits if not (lo <= len(c["subject"]) <= hi)]
    if bad:
        detail = "；".join(f"{c['hash'][:7]} 长度 {len(c['subject'])}" for c in bad[:3])
        return Result("message 长度", False, f"{len(bad)} 条不在 {lo}–{hi}：{detail}",
                      severity=severity)
    return Result("message 长度", True, f"都在 {lo}–{hi} 字符内", severity=severity)


def base_branch(repo: Repo) -> str:
    """学生分叉的基线分支。

    课程文件里的规则是**导入期**就绑好参数的，那时候还没有 repo，
    所以 base 不能写死 —— 让规则自己判断 main / master。
    """
    for name in ("main", "master"):
        if name in repo.branches():
            return name
    return "HEAD"


def check_commit_count(repo: Repo, max_n: int, base: str | None = None,
                       rev: str = "HEAD") -> Result:
    """学生**自己加的**提交数不得超过 max_n。

    注意不能数 `git rev-list --count HEAD` —— 那会把仓库自带的历史也算进去，
    而仓库本身就有 13 个提交，一开始就超标了。
    正确的口径是从"分叉点"起的增量。
    """
    base = base or base_branch(repo)
    mb = repo.merge_base(base, rev)
    if mb is None:
        n = repo.commit_count(rev)
        return Result("提交数", True, f"数不了增量（没有共同祖先），共 {n} 个",
                      severity="warn")
    n = int(repo.git("rev-list", "--count", f"{mb}..{rev}"))
    if n > max_n:
        return Result("提交数", False,
                      f"你自己加了 {n} 个提交，超过上限 {max_n}", severity="warn")
    return Result("提交数", True, f"你自己加了 {n} 个提交（上限 {max_n}）",
                  severity="warn")


def check_no_artifacts(repo: Repo, rev: str = "HEAD") -> Result:
    """仓库里（含全部历史）不得有构建产物 / IDE 生成文件。"""
    hits: dict[str, str] = {}
    for commit in repo.commits(rev):
        for f in repo.files_changed(commit["hash"]):
            for pat in ARTIFACT_PATTERNS:
                if fnmatch.fnmatch(f, pat) or fnmatch.fnmatch(f, pat.lstrip("*/")):
                    hits.setdefault(f, commit["hash"][:7])
                    break
            if len(hits) >= 8:
                break
        if len(hits) >= 8:
            break
    if hits:
        detail = "；".join(f"{f}（{h}）" for f, h in list(hits.items())[:3])
        return Result("无构建产物入库", False, f"发现 {len(hits)}+ 个：{detail}")
    return Result("无构建产物入库", True, "历史中没有构建产物")


def check_ignores_artifacts(repo: Repo, samples: list[str]) -> Result:
    """构建产物在**将来出现时**会不会被 .gitignore 挡住。"""
    res = repo.is_ignored(samples)
    missing = [p for p, ok in res.items() if not ok]
    if missing:
        return Result("构建产物已被 ignore", False,
                      f"这些路径不会被忽略：{', '.join(missing[:3])}")
    return Result("构建产物已被 ignore", True, f"{len(samples)} 个样本路径都会被忽略")


def check_no_conflict_markers(repo: Repo, rev: str = "HEAD",
                              paths: list[str] | None = None) -> Result:
    """工作区与已提交内容里都不得残留冲突标记。

    `paths` 用来限定范围 —— 必须限定！任务书里就有一段**示例**冲突输出
    （`<<<<<<< HEAD` 那种），不限定的话会把文档自己判成冲突残留。
    """
    marker = re.compile(r"^(<{7}|={7}|>{7})(\s|$)", re.M)
    scope = list(paths) if paths else ["."]
    bad: list[str] = []

    # 已提交的内容。git grep 的输出形如 "HEAD:path"，把前缀去掉
    r = repo._run("grep", "-I", "-l", "-E", r"^(<{7}|={7}|>{7})( |$)",
                  rev, "--", *scope, check=False)
    if r.returncode == 0:
        for line in r.stdout.splitlines():
            bad.append(line.split(":", 1)[1] if ":" in line else line)

    # 工作区里还没提交的文件
    for f in repo.tracked_files(rev):
        if not any(f == sc or f.startswith(sc.rstrip("/") + "/") for sc in scope):
            continue
        p = repo.root / f
        if p.is_file():
            try:
                text = p.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            if marker.search(text):
                bad.append(f"{f}（未提交）")

    bad = sorted(set(bad))
    if bad:
        return Result("无冲突标记残留", False, f"{len(bad)} 个文件：{', '.join(bad[:3])}")
    return Result("无冲突标记残留", True, "工作区与历史中都没有冲突标记")


def check_branch_naming(repo: Repo, pattern: str) -> Result:
    """存在至少一个符合命名规范的任务分支。"""
    rx = re.compile(pattern)
    good = [b for b in repo.branches() if rx.match(b)]
    if not good:
        return Result("分支命名", False,
                      f"没有符合 {pattern} 的分支（现有：{', '.join(repo.branches()[:5])}）")
    return Result("分支命名", True, f"存在合规分支：{', '.join(good[:3])}")


def check_branch_has_work(repo: Repo, pattern: str, base: str | None = None) -> Result:
    """合规分支上要有实质提交（不是空分支）。"""
    base = base or base_branch(repo)
    rx = re.compile(pattern)
    for b in repo.branches():
        if not rx.match(b):
            continue
        mb = repo.merge_base(b, base)
        if mb is None:
            # 没有共同祖先（比如 base 不存在），退化成"分支上有提交吗"
            n = repo.commit_count(b)
            if n > 0:
                return Result("分支上有提交", True, f"{b} 上有 {n} 个提交")
            continue
        n = int(repo.git("rev-list", "--count", f"{mb}..{b}"))
        if n > 0:
            return Result("分支上有提交", True, f"{b} 上有 {n} 个提交")
    return Result("分支上有提交", False, "合规分支上没有实质提交（是空分支）")


def check_merge_happened(repo: Repo, rev: str = "HEAD") -> Result:
    """历史上发生过合并（merge commit 或可看出的分叉合流）。"""
    merges = repo.merge_commits(rev)
    if merges:
        return Result("发生过合并", True, f"{len(merges)} 个 merge commit")
    return Result("发生过合并", False, "历史里没有 merge commit")


def check_pushed(repo: Repo, branch: str | None = None,
                 remote: str = "origin") -> Result:
    """当前分支（或指定分支）已经推送到远端。"""
    branch = branch or repo.current_branch()
    if not repo.has_remote(remote):
        return Result("已推送到远端", False, f"没有名为 {remote} 的远端", severity="warn")
    remotes = repo.remote_branches()
    target = f"{remote}/{branch}"
    if target not in remotes:
        return Result("已推送到远端", False, f"远端没有 {target}", severity="warn")
    local = repo.git("rev-parse", branch)
    remote_sha = repo.git("rev-parse", target)
    if local == remote_sha:
        return Result("已推送到远端", True, f"{target} 与本地一致", severity="warn")
    if repo.is_ancestor(local, remote_sha):
        return Result("已推送到远端", False, f"{target} 比本地新（需要 pull）", severity="warn")
    return Result("已推送到远端", False, f"{target} 落后于本地（还没 push）", severity="warn")


def check_atomic_heuristic(repo: Repo, max_top_dirs: int = 3,
                           rev: str = "HEAD") -> Result:
    """启发式：单个 commit 不应同时改太多不相关的顶层目录。

    ⚠️ 这只能抓"一次提交动了 app/ 和 mcu/ 和 .github/"这种明显情况。
    **判断不了"这个 commit 在逻辑上是不是一件事"** —— 那需要语义理解。
    宁可漏判，不可误判。
    """
    worst = None
    for c in repo.commits(rev):
        if len(c["parents"]) >= 2:
            continue
        files = repo.files_changed(c["hash"])
        tops = {f.split("/")[0] for f in files if "/" in f}
        if worst is None or len(tops) > len(worst[1]):
            worst = (c, tops)
    if worst and len(worst[1]) > max_top_dirs:
        c, tops = worst
        return Result("atomic 启发式", False,
                      f"{c['hash'][:7]} {c['subject'][:24]!r} 跨了 {len(tops)} 个顶层目录："
                      f"{', '.join(sorted(tops)[:4])}",
                      severity="warn")
    return Result("atomic 启发式", True, "没有明显跨模块的巨型提交", severity="warn")


def check_path_unmodified(repo: Repo, path: str, rev: str = "HEAD",
                          name: str = "测试文件未被修改") -> Result:
    """某个路径下的原有文件，内容**语义上**没有被改过。

    用来保护测试文件：改测试让测试通过 = 任务没完成。
    对比基准取"最早引入该路径的提交"，所以不依赖外部参照物。

    两个关键设计：

    **① 忽略空白。** 学生做完 HW4 会用 clang-format 把整个工程重排一遍，
    测试文件也会被重新缩进 —— 那是**格式**变化，不是**断言**变化。
    逐字节比对会把正常操作判成作弊，所以这里把空白全部去掉再比。

    **② 同时查工作区和已提交内容。** 学生自查时改动往往还没提交，
    只查 HEAD 会漏。允许**新增**文件（多写测试是好事），只禁止改动原有文件。
    """
    first = repo.first_commit_adding(path, rev)
    if first is None:
        return Result(name, False, f"历史里找不到 {path}")

    def norm(text: str) -> str:
        """去掉所有空白字符 —— 只比"代码说了什么"，不比"怎么排版"。"""
        return re.sub(r"\s+", "", text)

    prefix = path.rstrip("/") + "/"
    original = [f for f in repo.tracked_files(first)
                if f == path or f.startswith(prefix)]
    if not original:
        return Result(name, False, f"{first[:7]} 里没有 {path} 下的文件")

    changed: list[str] = []
    for f in original:
        want = repo.show_file(first, f)
        if want is None:
            continue
        # ① 已提交内容
        now = repo.show_file(rev, f)
        if now is None:
            changed.append(f"{f}（被删掉了）")
            continue
        if norm(now) != norm(want):
            changed.append(f)
            continue
        # ② 工作区（未提交的改动也要抓）
        cur = repo.worktree_file(f)
        if cur is not None and norm(cur) != norm(want):
            changed.append(f"{f}（未提交）")

    if changed:
        return Result(name, False, f"被改动了：{', '.join(sorted(set(changed))[:3])}")
    return Result(name, True, f"{path} 下的测试与最初一致")

def check_file_contains(repo: Repo, path: str, needles: list[str],
                        rev: str = "HEAD", name: str | None = None) -> Result:
    """文件（工作区优先）里必须同时包含这些标识符。

    这是**语义检查**，不是文本匹配 —— 顺序、缩进、位置都不限。
    """
    label = name or f"{path} 包含 {' + '.join(needles)}"
    content = repo.worktree_file(path)
    if content is None:
        content = repo.show_file(rev, path)
    if content is None:
        return Result(label, False, f"读不到 {path}")
    missing = [n for n in needles if n not in content]
    if missing:
        return Result(label, False, f"缺少：{', '.join(missing)}")
    return Result(label, True, f"{' 和 '.join(needles)} 都在")


def check_worktree_clean(repo: Repo) -> Result:
    out = repo.git("status", "--porcelain")
    if out.strip():
        n = len(out.splitlines())
        return Result("工作区干净", False, f"还有 {n} 项未处理", severity="warn")
    return Result("工作区干净", True, "没有未提交的改动", severity="warn")
