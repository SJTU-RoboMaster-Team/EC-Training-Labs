#!/usr/bin/env python3
#!/usr/bin/env python3
# ⚠️ 这个文件由 lab/sync_grader.py 从 lab/gitscore.py 复制而来。
#    要改请改 lab/ 下的那份，然后重新同步 —— 不要直接改这里。
"""gitscore —— 通用 Git 仓库只读封装 + 规则库。

设计原则（见 lab/DESIGN.md §2）：
  · **纯标准库**，不依赖任何第三方包
  · **只读**：绝不修改被检查的仓库
  · 规则都是普通函数：输入 Repo，输出 Result
  · 与具体某一课无关 —— 下一门课换个 lesson 文件就能复用

这个文件不认识"Day 0"或"HW5"，那些在 grade.py 里。
"""

from __future__ import annotations

import fnmatch
import os
import re
import subprocess
from pathlib import Path

# ══════════════════════════════════════════════════════════════════
# 结果模型
# ══════════════════════════════════════════════════════════════════


class Result:
    """一条检查的结果。

    severity:
      "fail" —— 必修项，不过就是 FAIL
      "warn" —— 提示项，只显示，不影响结论
    """

    def __init__(self, name: str, ok: bool, detail: str = "", severity: str = "fail"):
        self.name = name
        self.ok = ok
        self.detail = detail
        self.severity = severity

    @property
    def blocking(self) -> bool:
        return self.severity == "fail" and not self.ok


class RepoError(Exception):
    """仓库本身有问题（不是 Git 仓库、路径不存在等）。"""


# ══════════════════════════════════════════════════════════════════
# 仓库封装
# ══════════════════════════════════════════════════════════════════


class Repo:
    """一个 Git 仓库的只读视图。

    所有操作都走 subprocess 调 git —— 不引第三方库，也不碰 .git 内部结构。
    """

    def __init__(self, path: str | os.PathLike):
        self.path = Path(path).resolve()
        if not self.path.exists():
            raise RepoError(f"路径不存在：{self.path}")
        if not (self.path / ".git").exists():
            raise RepoError(f"不是一个 Git 仓库（找不到 .git）：{self.path}")
        # 确认 git 可用
        r = self._run("rev-parse", "--git-dir", check=False)
        if r.returncode != 0:
            raise RepoError(f"git 无法识别这个仓库：{self.path}")

    # ---------- 底层 ----------

    def _run(self, *args: str, check: bool = True) -> subprocess.CompletedProcess:
        r = subprocess.run(
            ["git", "-C", str(self.path), *args],
            capture_output=True, text=True,
            encoding="utf-8", errors="replace",
        )
        if check and r.returncode != 0:
            raise RepoError(f"git {' '.join(args)} 失败：{r.stderr.strip()}")
        return r

    def git(self, *args: str) -> str:
        """跑一条 git 命令，返回 stdout（去掉末尾换行）。"""
        return self._run(*args).stdout.strip()

    def git_ok(self, *args: str) -> bool:
        """跑一条 git 命令，只关心成功与否。"""
        return self._run(*args, check=False).returncode == 0

    # ---------- 基本信息 ----------

    @property
    def head(self) -> str:
        return self.git("rev-parse", "HEAD")

    @property
    def root(self) -> Path:
        return Path(self.git("rev-parse", "--show-toplevel"))

    def current_branch(self) -> str:
        """当前分支名。detached HEAD 时返回 'HEAD'。"""
        return self.git("rev-parse", "--abbrev-ref", "HEAD")

    def branches(self) -> list[str]:
        out = self.git("for-each-ref", "--format=%(refname:short)", "refs/heads/")
        return [b for b in out.splitlines() if b]

    def remote_branches(self) -> list[str]:
        out = self.git("for-each-ref", "--format=%(refname:short)", "refs/remotes/")
        return [b for b in out.splitlines() if b and not b.endswith("/HEAD")]

    def has_remote(self, name: str = "origin") -> bool:
        return name in self.git("remote").splitlines()

    # ---------- 提交 ----------

    def commits(self, rev: str = "HEAD") -> list[dict]:
        """提交列表（新的在前）。每个元素含 hash / subject / body / author / date。"""
        # 用 \x1f 分隔字段、\x1e 分隔记录，避免 subject 里的换行干扰
        fmt = "%H\x1f%P\x1f%an\x1f%ae\x1f%ad\x1f%s\x1f%b\x1e"
        out = self.git("log", f"--format={fmt}", "--date=short", rev)
        result = []
        for rec in out.split("\x1e"):
            rec = rec.strip("\n")
            if not rec:
                continue
            parts = rec.split("\x1f")
            if len(parts) < 7:
                continue
            result.append({
                "hash": parts[0],
                "parents": [p for p in parts[1].split() if p],
                "author": parts[2],
                "email": parts[3],
                "date": parts[4],
                "subject": parts[5],
                "body": parts[6].strip(),
            })
        return result

    def merge_commits(self, rev: str = "HEAD") -> list[dict]:
        return [c for c in self.commits(rev) if len(c["parents"]) >= 2]

    def commit_count(self, rev: str = "HEAD") -> int:
        return int(self.git("rev-list", "--count", rev))

    def merge_base(self, a: str, b: str) -> str | None:
        r = self._run("merge-base", a, b, check=False)
        return r.stdout.strip() or None

    def course_author(self) -> str:
        """课程仓库自带历史所用的作者邮箱（根提交的作者）。

        用来回答「这条提交是不是学生自己做的」。

        为什么不按分支判断：学生完全可能直接往 main 上提交，也可能把作业
        放在别的分支上 —— 按分支判断这两种都会判错。
        为什么按身份判断：仓库自带的那十几个提交都是课程身份提交的，
        学生用的是自己的 git 身份，这是最直接的依据。

        注意这**不是防作弊**：学生真想把 user.email 改成课程身份也能改。
        但那已经不是"无意中蒙对"了，而是明确地伪造记录，不值得我们为它
        加任何机制。
        """
        out = self.git("log", "--format=%ae", "--reverse", "--max-parents=0", "HEAD")
        lines = [l.strip() for l in out.splitlines() if l.strip()]
        return lines[0] if lines else ""

    def own_commits(self, rev: str = "HEAD") -> list[dict]:
        """只要学生自己写的提交（按作者身份过滤掉仓库自带历史）。"""
        course = self.course_author()
        return [c for c in self.commits(rev) if c["email"] != course]

    def files_changed(self, commit_hash: str) -> list[str]:
        out = self.git("show", "--pretty=format:", "--name-only", commit_hash)
        return [f for f in out.splitlines() if f.strip()]

    def is_ancestor(self, a: str, b: str) -> bool:
        return self.git_ok("merge-base", "--is-ancestor", a, b)

    # ---------- 内容 ----------

    def tracked_files(self, rev: str = "HEAD") -> list[str]:
        out = self.git("ls-tree", "-r", "--name-only", rev)
        return [f for f in out.splitlines() if f]

    def show_file(self, rev: str, path: str) -> str | None:
        """读某个 revision 下的文件内容；不存在返回 None。"""
        r = self._run("show", f"{rev}:{path}", check=False)
        return r.stdout if r.returncode == 0 else None

    def worktree_file(self, path: str) -> str | None:
        p = self.root / path
        if not p.is_file():
            return None
        try:
            return p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            return None

    def is_clean(self) -> bool:
        return not self.git("status", "--porcelain").strip()

    def tree_hash(self, rev: str, path: str) -> str | None:
        """某个目录/文件在某个 revision 下的 tree/blob hash。"""
        r = self._run("rev-parse", f"{rev}:{path}", check=False)
        return r.stdout.strip() if r.returncode == 0 else None

    def first_commit_adding(self, path: str, rev: str = "HEAD") -> str | None:
        """最早引入某个路径的提交（用 --diff-filter=A）。"""
        out = self.git("log", "--diff-filter=A", "--format=%H", rev, "--", path)
        lines = [l for l in out.splitlines() if l]
        return lines[-1] if lines else None

    def is_ignored(self, paths: list[str]) -> dict[str, bool]:
        """用 git check-ignore 判断这些路径会不会被忽略。

        用 --no-index，所以**路径不需要真的存在** —— 这正是我们要的：
        验证"以后构建产生的文件会不会被挡住"。
        """
        if not paths:
            return {}
        r = subprocess.run(
            ["git", "-C", str(self.path), "check-ignore", "--no-index", "--stdin"],
            input="\n".join(paths), capture_output=True, text=True,
            encoding="utf-8", errors="replace",
        )
        ignored = set(r.stdout.split("\n"))
        return {p: (p in ignored) for p in paths}


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


def check_commit_count(repo: Repo, max_n: int, base: str = "main",
                       rev: str = "HEAD") -> Result:
    """学生**自己加的**提交数不得超过 max_n。

    注意不能数 `git rev-list --count HEAD` —— 那会把仓库自带的历史也算进去，
    而仓库本身就有 13 个提交，一开始就超标了。
    正确的口径是从"分叉点"起的增量。
    """
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


def check_branch_has_work(repo: Repo, pattern: str, base: str = "main") -> Result:
    """合规分支上要有实质提交（不是空分支）。"""
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
