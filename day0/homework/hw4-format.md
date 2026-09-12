# HW4 · 格式化

前三份作业都在让代码**能用**。这一份让代码**整齐**——而且重点是**怎么把这件事提交得体面**。

这份作业看起来最简单，但它藏着一个直接影响 HW5 的坑：**格式化的范围。**

---

## 学习目标

1. 会在 IDE 里跑格式化，并让它读工程自带的那份 `.clang-format`
2. 理解**格式化改动不应该和逻辑改动混在一个 commit 里**
3. 理解**格式化的范围也是要选的**——顺手把整个仓库格式化，代价比你想的大

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

工程根目录有个 `.clang-format`，是从真实战队仓库抄来的：

```yaml
BasedOnStyle: LLVM
AccessModifierOffset: -4
AllowShortIfStatementsOnASingleLine: Never
ColumnLimit: 120
IndentWidth: 4
```

**但工程里的代码其实不符合它。** 这是真实项目里非常常见的情况：
配置早就定好了，只是没人统一跑过一遍。

> **你不需要装 clang-format 这个命令行工具。** 现在的 IDE 基本都内置了格式化，
> CLion 用的就是 clang-format，读的也是这个配置文件。见 Task 1。

---

## 任务

### Task 1 · 只格式化 `base/`

**在你的 IDE 里执行「重新格式化代码」这个动作。要格式化的范围是 `day0/project/base/` 这一个目录。**

快捷键各 IDE 不一样：

| IDE | 常见默认键位 |
| --- | --- |
| CLion / IntelliJ 系列 | `Ctrl + Alt + L` |
| VS Code | `Shift + Alt + F` |
| 其它 | 在菜单里找 **Code → Reformat Code** 之类 |

> **以你自己 IDE 的实际配置为准。** 有人装过 VS Code / Eclipse 的键位方案，
> 格式化就变成了 `Alt + Shift + F`；也有人用的是别的编辑器。
> 关键是找到那个「格式化」功能，不是背快捷键。

**操作方式：** 在项目树里**选中 `base` 这个目录**，再按格式化快捷键。

> CLion 用户额外确认一下：**Settings → Editor → Code Style** 里要勾上
> **Enable ClangFormat**（有些版本叫 "Use clang-format"），
> 否则它用的是 IDE 自己的规则，不是工程里那份 `.clang-format`。

#### 为什么只格式化 `base/`，不整个仓库一起格式化？

因为**你只需要为 `base/` 里的东西负责**：

- `base/` 是你在 HW2、HW3 里动过的目录（`math.h`、新建的 `angle.cpp`）
- `app/` `tests/` `mcu/` 是别人写的，你看都没看过

顺手把整个仓库格式化，会带来三个真实的代价：

1. **review 的人什么都看不出来。** 你只改了 20 行，diff 里却有 800 行缩进。
2. **`git blame` 废了。** 每一行都变成"上次是格式化那次改的"，真正的作者信息丢了。
3. **后面合并会打架。** 你把整个仓库重排了一遍，队友分支上的改动就落在一块
   完全不同的文本上——**HW5 你会亲手遇到这件事**，到时候回想一下这里。

> 这不是"不许格式化"，而是"**格式化和任何改动一样，要控制爆炸半径**"。
> 真要统一全仓库的风格，那是单独一件事、单独一次提交、单独一次讨论，
> 而不是你顺手按一下快捷键。

### Task 2 · 看懂这个 diff

```bash
git diff --stat
```

**先看规模**：改了哪几个文件、多少行。

再看"忽略空白之后还剩多少改动"：

```bash
git diff --ignore-all-space --stat
```

**怎么验证：**

- [ ] `git diff --stat` 显示 `base/` 下的文件被改了不少行
- [ ] `git diff --ignore-all-space --stat` 显示**几乎没有改动**

> 💡 **这两个数字的差，就是"排版"和"真的改了东西"的差。**
> 以后 review 别人的 PR 时，`--ignore-all-space` 是第一个该想到的开关。
>
> 如果第二个命令一个文件都没列出来，说明这次确实只动了排版——这正是我们要的。

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
git add base/
git diff --staged --stat
git commit
```

commit message 参考：

```text
style: apply clang-format to base/

base/ 下的代码没有统一跑过工程自带的 .clang-format。
本次只做格式化，不改变任何行为。
```

> ### 为什么要单独提交？
>
> 假设你把"格式化"和"修一个 bug"混在一个 commit 里，会发生什么：
>
> - 别人 review 时，**真正的 bug 修复被几百行缩进改动淹没了**
> - 以后想单独回退这个 bug 修复，会把格式化也一起退掉
> - `git blame` 会显示"这行是格式化那次改的"——**真正的作者信息丢了**
>
> 这就是讲义里 **atomic commit** 说的事情：
> **一个 commit 只表达一个逻辑变化。** "重新排版"是一个逻辑变化，
> "修 bug"是另一个。

**怎么验证：**

```bash
git log --oneline -3
git show --stat HEAD          # 这个 commit 应该只有格式化，而且只碰 base/
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
│ ✅ 代码符合 clang-format   base/ 缩进符合（4 空格）        │
│ ✅ 测试全部通过           clamp 4/4 · encoder 4/4          │
│ ✅ 有独立的格式化提交     style: apply clang-format …      │
│ ✅ commit message 格式    3 条都符合                       │
├────────────────────────────────────────────────────────────┤
│ 结论   PASS                                                │
└────────────────────────────────────────────────────────────┘
```

---

## 提交

把 `git diff --ignore-all-space --stat` 和 `git diff --stat` 两张图发到飞书群。

> 这两张图能同时说明两件事：你确实格式化了，而且**没改任何逻辑**。

---

## 评分

**只有 PASS / FAIL。**

- [ ] `base/` 下的 C++ 文件符合 `.clang-format`
- [ ] `test_encoder` 与 `test_clamp` **全部通过**
- [ ] 存在一个**独立的**格式化提交（message 里说明了只做格式化）
- [ ] 所有 commit message 符合 `type(scope): subject`

---

## 常见错误

| 症状 | 原因 | 怎么办 |
| --- | --- | --- |
| 格式化后测试挂了 | 误改了逻辑 | `git diff --ignore-all-space` 看真实改动，改回来 |
| 按了快捷键没反应 | 键位被改过 | 在菜单里找 Reformat Code；或看自己的键位映射 |
| CLion 格式化的结果和工程配置不一致 | 没勾 Enable ClangFormat | Settings → Editor → Code Style |
| `git status` 里冒出 `app/` `tests/` 一堆改动 | 格式化范围开成了整个项目 | `git restore app/ tests/ mcu/`，只保留 `base/` |
| 自查说"base/ 看起来没格式化过" | `base/` 里漏了文件 | 选中整个 `base` 目录再按，不要只选当前文件 |
| 格式化改动和别的改动混在一个 commit 了 | 提交前没分开 add | `git reset HEAD~1`，重新分别 add + commit |

---

## 参考

| 内容 | 在哪 |
| --- | --- |
| clang-format 是什么、怎么配 | Day 0 录播 · `../notes/03-clang-format.md` |
| atomic commit | Day 0 课件 Loop 2 |
| `git diff` 的各种开关 | Day 0 课件 Loop 1 |

---

## 做完之后

你现在手上有一个**测试全绿、提交历史清晰**的工程。

下一份作业（HW5）就是把这四份作业做的事情，在**真实的团队协作流程**里走一遍：
开分支、挑着提交、推上去、同步上游、解决冲突。

> **HW5 会检查你前面四份作业的提交信息。** 如果你在 HW1–HW4 里写过 `update`
> 这种 message，回去把它改好（`git rebase -i` 或加一条说明性的新提交）。
