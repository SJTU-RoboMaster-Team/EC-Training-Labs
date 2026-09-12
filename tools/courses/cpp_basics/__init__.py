# ⚠️ 这个文件由 lab/sync_grader.py 从 lab/courses/cpp_basics/__init__.py 复制而来。
#    要改请改 lab/ 下的那份，然后重新同步 —— 不要直接改这里。
"""cpp-basics 课程包。

作业定义在 `lessons.py`，static_assert 契约探针在 `probes/`。
这里只做转出，让引擎用同一种方式加载「单文件课程」和「包课程」。
"""

from .lessons import LESSONS, MODULE, MODULE_TITLE  # noqa: F401
