#!/usr/bin/env python3
"""rulelib.base —— 引擎与规则共用的底座。

只有三样东西：

  Result      一条检查的结果（PASS / FAIL / 提示）
  Repo        一个 Git 仓库的**只读**视图
  RepoError   仓库本身有问题（路径不存在、不是 Git 仓库……）
  R()         把「规则函数 + 参数」绑成只需要 repo 的可调用对象

规则模块（`git.py` / `code.py`）从这里 import，课程文件从规则模块 import。
依赖方向是单向的：base ← 规则 ← 课程 ← 引擎。

设计原则（见 lab/DESIGN.md §2）：
  · **纯标准库**，不依赖任何第三方包
  · **只读**：绝不修改被检查的仓库
"""

from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path

# ══════════════════════════════════════════════════════════════════
# 结果模型
# ══════════════════════════════════════════════════════════════════


class Result:
    """一条检查的结果。**三种状态**，不是两种。

    severity:
      "fail" —— 必修项，不过就是 FAIL
      "warn" —— 提示项，只显示，不影响结论

    skipped:
      True 表示「因为前面的检查没过，这条没跑」。
      为什么要有这个状态：学生最常见的情况是**编译都没过**。
      如果照常往下跑，他会看到十几条 FAIL —— 大部分是编译失败的连带结果，
      真正要修的只有第一条。跳过时显示成灰色的「跳过」，并说明原因。

      （这个做法来自 CS50 check50：它的 `passed` 是 true / false / null，
        null 就是"因依赖没过而跳过"。我们只用一个布尔就够，不需要依赖图。）
    """

    def __init__(self, name: str, ok: bool, detail: str = "", severity: str = "fail",
                 skipped: bool = False):
        self.name = name
        self.ok = ok
        self.detail = detail
        self.severity = severity
        self.skipped = skipped

    @property
    def blocking(self) -> bool:
        return self.severity == "fail" and not self.ok and not self.skipped

    @staticmethod
    def skip(name: str, why: str = "前面的检查没过") -> "Result":
        return Result(name, False, f"跳过（{why}）", severity="warn", skipped=True)


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


def R(fn, *args, **kwargs):
    """把「规则函数 + 参数」绑成一个只需要 repo 的可调用对象。

    课程文件里这样写：

        LESSONS = {"hw1": ("HW1 · 把项目跑起来", [
            R(code.build, PROJECT),
            R(git.check_worktree_clean),
        ])}

    引擎拿到列表后逐个 `rule(repo)` 调用。
    规则函数本身保持 `f(repo, ...) -> Result` 的普通签名，不需要为引擎改形。
    """
    label = kwargs.pop("_label", None)
    bound = lambda repo: fn(repo, *args, **kwargs)      # noqa: E731
    # 保留原函数名 —— 规则内部抛异常、或者被跳过时，要能看出是哪一条。
    # `_label` 可以覆盖它，写成学生看得懂的话。
    bound.__name__ = label or getattr(fn, "__name__", "rule")
    return bound
