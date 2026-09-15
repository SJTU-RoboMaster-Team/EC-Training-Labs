#!/usr/bin/env python3
"""selftest.py —— Autograder 的自检。

**它检查的是 grader，不是学生。** 这两件事必须分清：

  · 学生的作业对不对 → `tools/grade.py <作业> <他的仓库>`
  · grader 还对不对劲   → 这个文件

存在理由：`grade.py:load_courses()` 对坏掉的课程文件是**容错**的 ——
它打印一行警告然后跳过那个模块。这在学生机器上是对的（一门课坏了
不该让另一门课也用不了），但后果是**这门课会静默消失**：学生
`--list` 看不到它，也不会有任何人收到通知。所以需要一条会自动跑的检查。

设计约束（为什么写成这样）：

  1. **不引入测试框架。** 只用标准库 + `assert`，仓库里现在没有任何
     requirements/dev-deps，加一套 pytest 是新的维护面。
  2. **不重复实现评分逻辑。** 本文件通过 `grade.py --json` 的既有契约
     观察结果 —— 那份 JSON 本来就是给机器消费者准备的
     （见 `grade.py` 模块 docstring），这里只是第一个真正的机器消费者。
  3. **只断言"会真的坏掉"的东西。** 断言的是不变量，不是当前数字：
     学生该失败的地方必须**继续失败**，该通过的地方必须**继续通过**。
     学生把作业做对之后，hw1/hw3 的结论当然会变 —— 那是预期行为，
     不是这条 CI 要守的东西（见下面"注意"）。

用法：

    python tools/selftest.py          # 从仓库根目录
    python tools/selftest.py --verbose

退出码：0 = 全部通过，1 = 有断言失败，2 = 环境问题（缺工具/跑不起来）

注意：本自检对**未完成的** starter 仓库断言 `hw3` FAIL。等到所有学生都
做完了、有人把答案合进 main 之后，这条断言需要跟着改成"hw3 PASS"。
那是课程往前走了一步，不是回归。
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GRADE = Path(__file__).resolve().parent / "grade.py"

# 两份 starter 仓库上的已知事实。改动课程或 starter 时这两个集合会变，
# 那时**改这里**，而不是把断言删掉。
#
# 注意：这里**只列 hw3 自己那条线的三个阻断项**（测试 / 符号实现 / 书面回答），
# 不列 `message 格式`。原因不是嫌它烦，而是那条规则查的是**整个仓库的提交历史**
# （`git.check_message_format` 的 `own_only` 默认 False），它的成败取决于仓库里
# 所有人写过的每一句 commit message，与 hw3 要修的三项**没有关系**。
# 把它算进"hw3 的失败集"，一个全新的、完全合法的提交（例如本分支引入 workflow
# 的那一条）就会把 hw3 判成回归 —— 这正是本自检第一次运行时给出的假警。
# 判据是"该失败的语义项是否仍在失败"，不是"失败总数是否等于 3"。
STARTER_FAILS_HW3 = {"测试全部通过", "wrap_angle_deg 有实现", "回答了3个问题"}
EXPECTED_LESSONS = {"hw1", "hw2", "hw3", "hw4", "hw5", "cpp1", "cpp2", "cpp3", "cpp4"}

failures: list[str] = []


def say(verbose: bool, message: str) -> None:
    if verbose:
        print(f"   {message}")


def check(name: str, condition: bool, detail: str = "") -> None:
    if condition:
        print(f"✅ {name}")
    else:
        print(f"❌ {name}" + (f"：{detail}" if detail else ""))
        failures.append(name)


def run_grader(lesson: str, *extra: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(GRADE), lesson, str(ROOT), *extra],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(ROOT),
    )


def grader_json(lesson: str) -> dict:
    """跑一次 grader 并解析 JSON。非 0/1 退出码一律当环境问题。"""
    done = run_grader(lesson, "--json")
    if done.returncode not in (0, 1):
        raise RuntimeError(
            f"{lesson}: grader 退出码 {done.returncode}（环境问题）\n"
            f"{(done.stderr or '').strip()[:400]}"
        )
    try:
        return json.loads(done.stdout)
    except json.JSONDecodeError as error:
        raise RuntimeError(f"{lesson}: JSON 解析失败：{error}") from error


def blocking_names(payload: dict) -> set[str]:
    return {item["name"] for item in payload["results"]
            if not item["ok"] and item["severity"] == "fail"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()
    verbose = args.verbose

    # ── 1. 课程加载 ────────────────────────────────────────────────
    # load_courses() 会跳过坏掉的模块，所以 --list 退出码是 0 也可能
    # 已经少了一门课。这里查的是**清单本身**，不是退出码。
    print("① 课程加载")
    listed = subprocess.run(
        [sys.executable, str(GRADE), "--list"],
        capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=str(ROOT),
    )
    missing = [lesson for lesson in sorted(EXPECTED_LESSONS)
               if lesson not in listed.stdout]
    check("9 份作业全部加载", not missing,
          f"缺 {missing}；stderr={(listed.stderr or '').strip()[:200]}")
    check("没有课程加载警告", "加载失败" not in listed.stdout + (listed.stderr or ""),
          "有课程文件被跳过，见上一条")
    say(verbose, f"退出码 {listed.returncode}")

    # ── 2. --json 契约 ────────────────────────────────────────────
    # 这是 CI 和别的工具消费 grader 的唯一stable接口，先钉住它的形状。
    print("② --json 契约")
    payload = grader_json("hw3")
    for key in ("lesson", "module", "verdict", "results", "branch"):
        check(f"JSON 有 {key}", key in payload)
    check("结果项字段完整",
          all({"name", "ok", "detail", "severity"} <= set(item)
              for item in payload.get("results", [])),
          "有结果项缺字段")

    # ── 3. starter 上 hw3 的三个语义阻断项必须继续 FAIL ────────────
    print("③ starter 仓库的 hw3 行为")
    check("hw3 结论为 FAIL", payload.get("verdict") == "FAIL",
          f"实际 {payload.get('verdict')}")
    actual = blocking_names(payload)
    missing = STARTER_FAILS_HW3 - actual
    check("hw3 的三个已知阻断项仍在失败", not missing,
          f"grader 不再抓 {sorted(missing)} —— 学生做错也看不出来")
    # 只断言"少了"这一个方向。多了不判失败：hw3 的必修项里包含
    # `message 格式`，它查全仓历史，多出来的失败不一定与 hw3 有关（见文件头）。
    extra = actual - STARTER_FAILS_HW3
    if extra:
        say(True, f"另有 {sorted(extra)} 也在失败（多数来自全仓提交历史，不算回归）")

    # ── 4. hw1 必须能构建（工具链可用性的端到端证据）────────────────
    print("④ 构建与测试")
    if not shutil.which("cmake"):
        check("cmake 可用", False, "CI 里应装 cmake；本机跑时请先装")
    else:
        hw1 = grader_json("hw1")
        check("hw1 结论为 PASS", hw1.get("verdict") == "PASS",
              f"实际 {hw1.get('verdict')}，未通过 "
              f"{sorted(blocking_names(hw1))}")

    # ── 5. 学生路径也不能崩 ───────────────────────────────────────
    # 课程还可以用 git URL 验收；这条只验证本地路径这一侧不会抛异常。
    print("⑤ 学生侧路径")
    for lesson in ("hw2", "hw4", "cpp1"):
        try:
            one = grader_json(lesson)
        except RuntimeError as error:
            check(f"{lesson} 能跑完", False, str(error)[:200])
            continue
        check(f"{lesson} 能跑完", one.get("verdict") in {"PASS", "FAIL"},
              f"结论异常：{one.get('verdict')}")

    print()
    if failures:
        print(f"❌ 自检未通过：{len(failures)} 项")
        for name in failures:
            print(f"   · {name}")
        return 1
    print("✅ 自检全部通过")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except RuntimeError as error:
        print(f"!! {error}", file=sys.stderr)
        sys.exit(2)
