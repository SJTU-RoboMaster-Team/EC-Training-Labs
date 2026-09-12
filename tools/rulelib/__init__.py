# ⚠️ 这个文件由 lab/sync_grader.py 从 lab/rulelib/__init__.py 复制而来。
#    要改请改 lab/ 下的那份，然后重新同步 —— 不要直接改这里。
"""rulelib —— 可复用的检查规则库。

    base.py   结果模型 + 仓库只读封装（规则与引擎共用）
    git.py    Git 仓库类规则（提交、分支、合并、冲突……）
    code.py   C/C++ 代码类规则（构建、测试、符号、契约、源码扫描）

换一门课不需要改这里；改这里要保证现有课程仍然全绿（跑 `verify_chain.py`）。
"""

from . import base, code, git  # noqa: F401
