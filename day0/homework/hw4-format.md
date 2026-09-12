# HW4 · 格式化

前三份作业都在让代码**能用**。这一份让代码**整齐**——而且重点是**怎么把这件事提交得体面**。

这份作业看起来最简单，但它藏着一个直接影响 HW5 的坑。

---

## 学习目标

1. 会用工程的 `.clang-format` 配置统一代码风格（CLion 内置支持，不用另外装）
2. 理解**格式化改动不应该和逻辑改动混在一个 commit 里**
3. 看懂一个"大 diff"里哪些是真正的改动、哪些只是排版

---

## 开始之前

- [ ] 完成了 HW3，工程能构建、测试全绿
- [ ] `git status` 干净

---

## 获取代码

```bash
cd EC-Training-Labs/day0/project
git switch main
git pull
```

> ⚠️ **工作目录：后面所有命令都在 `day0/project/` 里执行。**

---

## 背景：这个工程有风格配置，但没被执行过

工程根目录有个 `.clang-format` 文件，是从真实战队仓库抄来的：

```yaml
BasedOnStyle: LLVM
AccessModifierOffset: -4
AllowShortIfStatementsOnASingleLine: Never
ColumnLimit: 120
...
```

**但工程里的代码其实不符合它。** 这是真实项目里非常常见的情况：
配置早就定好了，只是没人统一跑过一遍。

> **你不需要装 clang-format。** 现在的 IDE 基本都内置了格式化，
> CLion 用的就是 clang-format，读的也是这个配置文件。见 Task 1。

---

## 任务

### Task 1 · 在 IDE 里跑一遍格式化

**在你的 IDE 里执行「重新格式化代码」这个动作。** 快捷键各 IDE 不一样：

| IDE | 默认快捷键 |
| --- | --- |
| CLion / IntelliJ 系列 | `Ctrl + Alt + L` |
| VS Code | `Shift + Alt + F` |
| 其它 | 在菜单里找 **Code → Reformat Code** 之类 |

> **以你自己 IDE 的实际配置为准。** 有人改过键位映射，也有人用的是别的编辑器——
> 关键是找到那个「格式化当前文件 / 整个项目」的功能，不是背快捷键。
>
> CLion 用户额外确认一下：**Settings → Editor → Code Style** 里要勾上
> **Enable ClangFormat**（有些版本叫 "Use clang-format"），
> 否则它用的是 IDE 自己的规则，不是工程里那份 `.clang-format`。

**要格式化的范围：** `day0/project/app/`、`base/`、`tests/` 三个目录下的所有 C++ 文件。

> 在项目树里**选中这三个目录**，再按格式化快捷键，一次搞定。

### Task 2 · 看懂这个 diff

```bash
git diff --stat
```

**你应该看到几乎所有源文件都被改了**，行数很大。

**先别慌。** 用这个命令看"忽略空白之后还剩多少改动"：

```bash
git diff --ignore-all-space --stat
```

**怎么验证：**

- [ ] `git diff --stat` 显示很多文件、很多行
- [ ] `git diff --ignore-all-space --stat` 显示的改动**少得多**

> 💡 **这两个数字的差，就是"排版"和"真的改了东西"的差。**
> 以后 review 别人的 PR 时，`--ignore-all-space` 是第一个该想到的开关。

---

### Task 3 · 确认格式化没弄坏东西

```bash
python tools/build.py
```

**期望：** 还是全绿。

**怎么验证：**

- [ ] `test_encoder` 4/4
- [ ] `test_clamp` 4/4

> ⚠️ **格式化不该改变程序行为。** 如果测试挂了，说明你误改了逻辑
> （比如把 `d < -180.0f` 改成了 `d < 180.0f`）。

---

### Task 4 · 单独提交它（**这份作业的重点**）

**不要**把这些排版改动和别的改动混在一起提交。

```bash
git status
git add app/ base/ tests/
git diff --staged --stat
git commit
```

commit message 参考：

```text
style: apply clang-format to the project

工程里一直有 .clang-format 配置，但代码没有统一跑过。
本次只做格式化，不改变任何行为。
```

> ### 为什么要单独提交？
>
> 假设你把"格式化"和"修一个 bug"混在一个 commit 里，会发生什么：
>
> - 别人 review 时，**真正的 bug 修复被几千行缩进改动淹没了**
> - 以后想单独回退这个 bug 修复，会把格式化也一起退掉
> - `git blame` 会显示"这行是格式化那次改的"——**真正的作者信息丢了**
>
> 这就是讲义里 **atomic commit** 说的事情：
> **一个 commit 只表达一个逻辑变化。** "重新排版"是一个逻辑变化，
> "修 bug"是另一个。

**怎么验证：**

```bash
git log --oneline -3
git show --stat HEAD          # 这个 commit 应该只有格式化
```

---

### Task 5 · 收尾

```bash
git push
git status                    # 干净
```

---

## 自查

```bash
# 在你仓库的根目录下（就是 EC-Training-Labs/ 这一层）
python tools/grade.py hw4 .
```

> **`grade.py` 就在你的仓库里**（`tools/grade.py`）。它和老师用的是同一份代码，
> 所以**你跑出什么结果，老师就验收什么结果**。

**期望看到：**

```text
┌────────────────────────────────────────────────────────────┐
│ HW4 · 格式化                                               │
├────────────────────────────────────────────────────────────┤
│ ✅ 代码符合 clang-format   缩进看起来符合（4 空格）        │
│ ✅ 测试全部通过           clamp 4/4 · encoder 4/4          │
│ ✅ 有独立的格式化提交     style: apply clang-format …      │
├────────────────────────────────────────────────────────────┤
│ 结论   PASS                                                │
└────────────────────────────────────────────────────────────┘
```

---

## 提交

把 `git diff --ignore-all-space --stat` 的截图发到飞书群。

> 这张图能同时说明两件事：你确实格式化了整个工程，而且**没改任何逻辑**。

---

## 评分

**只有 PASS / FAIL。**

- [ ] `app/`、`base/`、`tests/` 下的 C++ 文件都符合 `.clang-format`
- [ ] `test_encoder` 与 `test_clamp` **全部通过**
- [ ] 存在一个**独立的**格式化提交（message 里说明了只做格式化）

---

## 常见错误

| 症状 | 原因 | 怎么办 |
| --- | --- | --- |
| 格式化后测试挂了 | 误改了逻辑 | `git diff --ignore-all-space` 看真实改动，改回来 |
| 按了快捷键没反应 | 键位被改过 | 在菜单里找 Reformat Code；或看自己的键位映射 |
| CLion 格式化的结果和工程配置不一致 | 没勾 Enable ClangFormat | Settings → Editor → Code Style |
| 格式化只改了部分文件 | 只选中了部分目录 | 全选 `app/` `base/` `tests/` 再按 |
| 自查说"看起来没格式化过" | 格式化范围漏了文件 | 确认三个目录都选中了 |
| 格式化改动和别的改动混在一个 commit 了 | 提交前没分开 add | `git reset HEAD~1`，重新分别 add + commit |

---

## 参考

| 内容 | 在哪 |
| --- | --- |
| clang-format 是什么、怎么配 | Day 0 录播 · `Tools/03-clang-format.md` |
| atomic commit | Day 0 课件 Loop 2 |
| `git diff` 的各种开关 | Day 0 课件 Loop 1 |

---

## 做完之后

你现在手上有一个**整整齐齐、测试全绿、提交历史清晰**的工程。

下一份作业（HW5）就是把这四份作业做的事情，在**真实的团队协作流程**里走一遍：
开分支、挑着提交、推上去、同步上游、解决冲突。

**HW5 会检查你前面四份作业的提交信息。** 如果你在 HW1–HW4 里写过 `update`
这种 message，回去把它改好（`git rebase -i` 或加一条说明性的新提交）。
