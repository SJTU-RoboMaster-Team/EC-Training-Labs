# ⚠️ 这个文件由 lab/sync_grader.py 从 lab/courses/__init__.py 复制而来。
#    要改请改那份，然后重新同步 —— 不要直接改这里。
"""courses —— 每门课一个文件。

一个课程文件里给出三样东西：

    MODULE        模块名（如 "day0-git"），--list 按它分组
    MODULE_TITLE  给人看的模块标题
    LESSONS       {作业编号: (标题, [规则...])}

规则用 `R(函数, 参数...)` 绑好，引擎逐个 `rule(repo)` 调用。
加一门课 = 在这里加一个 .py（或一个包），**不需要改 grade.py 或 rulelib/**。

两种写法都行：

    courses/can_lab.py              单文件，课程简单时用这个
    courses/cpp_basics/__init__.py  包，课程还要带探针/数据文件时用这个
    courses/cpp_basics/lessons.py
    courses/cpp_basics/probes/*.cpp

包的话，`__init__.py` 里把 `MODULE` / `MODULE_TITLE` / `LESSONS` 转出来即可。
"""
