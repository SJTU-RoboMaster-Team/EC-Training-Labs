# HW5 · Git 工作流

前四份作业你一直在**改代码**：跑起来、修 bug、搞懂编译链接、格式化。
但你每次都是直接 `git commit` 到 `main` 上——**那是一个人在玩**。

这一份不一样：你要像个团队一样工作。

> **同一件事，两种做法**
>
> | | 你前面做的 | 这一份要做的 |
> | --- | --- | --- |
> | 在哪工作 | 直接在 `main` | **开一个任务分支** |
> | 改动从哪来 | 老师指哪改哪 | **你自己从 TODO 里挑** |
> | 提交完就完了吗 | 是 | **要推上去、要同步别人的改动** |
> | 遇到冲突 | 没遇到过 | **解决一次真的** |
>
> Task 9 里你要合并的 `DROP_MODE`，是**老师真的推在上游分支上的代码**，
> 不是模拟出来的。

---

## 学习目标

1. 用**任务分支**隔离自己的工作，理解"分支只是一个指针"
2. 从真实 TODO 出发做改动，**先看清自己改了什么，再决定怎么提交**
3. 把多个不相关的改动**拆成多个 atomic commit**
4. 把分支**推送**到自己的仓库
5. **同步上游**——把别人的改动合进自己的分支
6. 解决一次**真实的合并冲突**，理解"冲突 ≠ 选一边"
7. 合并之后**重新验证**（合并成功 ≠ 程序正确）

---

## 开始之前

逐条确认。**有一条没打勾就先别往下做。**

- [ ] 完成了 HW1–HW4，`python tools/build.py` 全绿（`encoder 4/4 · clamp 4/4`）
- [ ] `git status` 显示工作区干净
- [ ] `git log --oneline` 能看到你自己 HW2–HW4 的提交
- [ ] `ssh -T git@github.com` 返回 `Hi <你的用户名>!`
- [ ] 你的仓库是 **public**

---

## 获取代码

```bash
cd EC-Training-Labs
git switch main
git pull

# 把老师的仓库加成第二个远端 —— Task 9 要用
git remote add upstream git@github.com:SJTU-RoboMaster-Team/EC-Training-Labs.git
git remote -v          # 应该看到 origin（你的）和 upstream（老师的）
```

> ⚠️ **工作目录：这一份作业的 Git 命令都在 `EC-Training-Labs/`（仓库根）下敲，
> 但改代码要进 `day0/project/`。** 每一步都会写清楚。

---

## 任务

### Task 1 · 先看清你现在有什么

```bash
git status
git log --oneline --graph -8
```

**你应该看到：** 工作区干净，历史里有你 HW2（修编码器）、HW3（抽出 `wrap_angle_deg`）、
HW4（格式化）的提交。

**怎么验证：** 你能说出"我前面三份作业分别提交了什么"。

> 这三条提交现在都躺在 `main` 上。**从这一份作业开始，不要再往 `main` 上提交了。**

---

### Task 2 · 开一个任务分支

```bash
git switch -c fix/pickup-todos
```

分支名格式 `<type>/<what>`，`<type>` 从 `feat` `fix` `refactor` `tune` `exp` 里选。

**怎么验证：**

```bash
git branch            # 当前分支前面有 *
git status            # On branch fix/pickup-todos
```

---

### Task 3 · 找到三个 TODO，读懂它们

有人在这个项目里留了三个待办，散在三个文件里。**它们互不相关**——
正好用来练"把不同的改动拆开提交"。

```bash
cd day0/project
grep -rn "TODO(hw5" app/
```

**你应该找到三条：**

| 标记 | 文件 | 说的是什么 |
| --- | --- | --- |
| `TODO(hw5-a)` | `app/control.cpp` | 夹爪默认速度偏慢，要按当前值的 1.5 倍调 |
| `TODO(hw5-b)` | `app/clamp.cpp` | 标定期间不该做阻力判断，否则误判成夹住 |
| `TODO(hw5-c)` | `app/arm.h` | 标定流程需要一个独立的工作模式 `CALIBRATE` |

**怎么验证：** 你能用自己的话说出这三件事分别在解决什么问题。

> 💡 **先读懂再动手。** 你等下要把它们**分三次**提交，
> 而每条 commit message 都得说清"为什么改"——读不懂就写不出来。

---

### Task 4 · 把这三处都改了（先不要提交）

- **`app/control.cpp`**：把 `kDefaultClampSpeed` 按 TODO 说的调（当前值的 **1.5 倍**）
- **`app/clamp.cpp`**：让标定期间跳过阻力判断。
  文件里已经有 `is_calibrating_` 成员和 `beginCalibration()` / `endCalibration()`，用它
- **`app/arm.h`**：在 `Mode_e` 枚举末尾加上 `CALIBRATE`

改完把三处 `TODO(hw5-*)` 注释删掉——事情做完了，TODO 就该消失。

**怎么验证：**

```bash
python tools/build.py
```

- [ ] 构建成功
- [ ] `test_encoder` 4/4，`test_clamp` 4/4

> ⚠️ 如果 `test_clamp` 挂了，说明你把阻力判断改坏了。
> 想一想：`is_calibrating_` 默认是 `false`，那"标定期间跳过"该怎么写才不影响正常情况？

---

### Task 5 · 看清你自己改了什么

**这一步不能省。** 提交之前，你必须知道自己在提交什么。

```bash
git status
git diff
```

**你应该看到：** 三个文件被修改，每一个对应一件独立的事。

**怎么验证：** 你能回答——

- [ ] 改了哪几个文件？
- [ ] 每个文件改的是哪一件事？
- [ ] 这三件事之间有关系吗？

> **关系是"没有关系"。** 调夹爪速度、修标定误判、加一个工作模式——
> 这是三件独立的事。所以它们应该是**三个提交**，不是一个。

---

### Task 6 · 把生成文件挡在外面

Keil 一打开工程就会生成一堆文件。你现在没开 Keil，用脚本模拟一下：

```bash
python tools/make_generated_files.py
git status
```

**你应该看到** `mcu/stm32f407/MDK-ARM/` 下面冒出来几个 Git 不认识的文件。

**它们不该进版本库**——每次打开 Keil 都会变，提交进去只会制造无意义的 diff 和冲突。

> 你可能想问：那 `build/` 呢？构建目录不是更不该进库？
> 打开 `day0/project/.gitignore` 看一眼——**它已经在里面了**：
>
> ```gitignore
> # 构建目录
> build/
> cmake-build-*/
> ```
>
> 所以 `git status` 里从来没出现过 `build/`。
> **这次的缺口只有 Keil 那几种文件**——一个仓库的 ignore 规则齐不齐，
> 是被人一条条踩坑补出来的，不是一次写全的。

**打开 `day0/project/.gitignore`，把缺的规则补上：**

```gitignore
# Keil 生成文件
*DebugConfig*
**/RTE/**
*uvguix*
```

**怎么验证：**

```bash
git status
```

**期望：** `mcu/` 下面那几个文件从 untracked 列表里**消失了**，
只剩下那三个 `modified`。

> **这三条 Keil 规则不是我编的**，是真实仓库 `.gitignore` 里的原文。
> 真实项目里你也会遇到同样的事：先看到一堆陌生文件，再判断哪些该提交。
> 我们统计过战队几个仓库的合并冲突，**Keil 的 `*.uvprojx` / `*.uvoptx`
> 占了 15%** —— 就是没 ignore 干净闹的。

---

### Task 7 · 整理成四个提交

现在工作区里有**四件事**：三条 ignore 规则（算一件），和三个代码改动。

**一个一个提交。**

```bash
# ① 先提交 .gitignore
git add day0/project/.gitignore
git diff --staged
git commit -m "chore(gitignore): ignore Keil generated files and build output"

# ② 夹爪速度
git add day0/project/app/control.cpp
git diff --staged
git commit -m "tune(clamp): raise default clamp speed by 1.5x"

# ③ 标定期间不判阻力
git add day0/project/app/clamp.cpp
git diff --staged
git commit -m "fix(clamp): skip resistance check while calibrating"

# ④ 加工作模式
git add day0/project/app/arm.h
git diff --staged
git commit -m "feat(arm): add CALIBRATE mode for the calibration flow"
```

上面四条只是**参考**——message 要你自己写，但必须说清"改了什么、为什么"。

**怎么验证：**

```bash
git log --oneline -5          # 看到你刚做的四条
git status                    # working tree clean
```

> ### 为什么不一次性 `git add .` 然后一个提交？
>
> 因为那是**四个逻辑变化**。混在一起的话：
> - 以后想单独回退"夹爪速度"，会把 ignore 规则和另外两个修复也一起退掉
> - review 的人看到一坨 diff，说不清你在干什么
> - `git log` 里那一条 message 根本没法同时描述四件事
>
> 这就是讲义里 **atomic commit** 的意思：
> **一个 commit 只表达一个逻辑变化。**

---

### Task 8 · 推送

```bash
git push -u origin fix/pickup-todos
```

**怎么验证：** 打开 `https://github.com/<你的用户名>/EC-Training-Labs`，
在分支下拉框里能看到 `fix/pickup-todos`。

> **本地 commit 不是团队备份。** 到这一步为止，你的工作只有你自己看得见。

---

### Task 9 · 同步上游（制造一次真实冲突）

**场景**：老师在 upstream 上开了一个功能分支 `drop-mode`，给机械臂加了"存取矿"模式。
这个改动**恰好也动到了 `Mode_e` 枚举的末尾**——和你在 Task 4 里加 `CALIBRATE` 的位置一样。

```bash
git fetch upstream
git log --oneline --graph upstream/drop-mode -5    # 看看老师加了什么
git merge upstream/drop-mode
```

**你应该会看到冲突**（`CONFLICT`），在 `app/arm.h`。

```bash
git status
```

**怎么验证：** `git status` 显示 `Unmerged paths`，里面是 `app/arm.h`。

> **这不是出错，也不是你哪里做坏了。**
> 冲突的含义是：**你和对方真的改了同一个地方，Git 没法替你决定。**

---

### Task 10 · 解决冲突

打开 `app/arm.h`，你会看到：

```cpp
  STORAGE_BACK,
<<<<<<< HEAD
  CALIBRATE,
=======
  DROP_MODE,
>>>>>>> upstream/drop-mode
};
```

**关键认知：冲突不是"选一边"，而是"想清楚两边各自要什么"。**

- 你加 `CALIBRATE` 是为了标定流程
- 老师加 `DROP_MODE` 是为了存取矿

**这两个都要保留。** 冲突的原因是它们加在了同一行位置，**不是它们互相矛盾**。

编辑 `app/arm.h`，把两边都留下（顺序不限）：

```cpp
  STORAGE_BACK,
  CALIBRATE,        // 你的
  DROP_MODE,        // 上游的
};
```

然后：

```bash
git diff                                    # ★ 确认没有残留的冲突标记
cd day0/project && python tools/build.py    # ★ 必须重新验证
cd ../..
git add day0/project/app/arm.h
git commit
```

merge commit 的 message 要写清**你做了什么决定**。

**怎么验证：**

```bash
git log --oneline --graph -8
```

**期望：** 能看到一个 merge commit（有两条线汇进来）。

> ⚠️ **合并成功 ≠ 程序正确。**
> Git 只能告诉你"文本层面合并完了"，它不知道你枚举值加得对不对。
> **所以上面的 `tools/build.py` 不能省。**

---

### Task 11 · 验证 + 收尾

```bash
cd day0/project && python tools/build.py && cd ../..
git push
git status
git log --oneline --graph -10
```

---

## 自查

```bash
# 在你仓库的根目录下（就是 EC-Training-Labs/ 这一层，
# 不是 day0/project/，也不是 day0/homework/）
python tools/grade.py hw5 .
```

> **`grade.py` 就在你的仓库里**（`tools/grade.py`）。它和老师用的是同一份代码，
> 所以**你跑出什么结果，老师就验收什么结果**。

**期望看到：**

```text
┌────────────────────────────────────────────────────────────┐
│ HW5 · Git 工作流                                           │
│ 仓库 /path/to/EC-Training-Labs                             │
│ 分支 fix/pickup-todos → main                               │
├────────────────────────────────────────────────────────────┤
│ ✅ 分支命名               存在合规分支：fix/pickup-todos   │
│ ✅ 分支上有提交           fix/pickup-todos 上有 5 个提交   │
│ ✅ message 格式           22/22 条合规                     │
│ ✅ message 黑名单         没有低信息量 message             │
│ ✅ 无构建产物入库         历史中没有构建产物               │
│ ✅ 无冲突标记残留         工作区与历史中都没有冲突标记     │
│ ✅ 测试文件未被修改       day0/project/tests 下的测试与…   │
│ ✅ 冲突保留双方意图       CALIBRATE 和 DROP_MODE 都在      │
│ ✅ 三个 TODO 都已处理     速度已调 / 标定判断已加          │
│ ✅ 发生过合并             1 个 merge commit                │
│ ✅ 测试全部通过           clamp 4/4 · encoder 4/4          │
│ ✅ 提交数                 你自己加了 5 个提交（上限 15）   │
│ ✅ message 长度           都在 10–72 字符内                │
│ ✅ atomic 启发式          没有明显跨模块的巨型提交         │
│ ✅ 工作区干净             没有未提交的改动                 │
│ ✅ 已推送到远端           origin/fix/pickup-todos 一致     │
├────────────────────────────────────────────────────────────┤
│ 结论   PASS    全部必修项通过                              │
└────────────────────────────────────────────────────────────┘
```

**如果 FAIL**，明细里会写清楚是哪一项没过——照着改，然后重跑，
**不要直接提交**。

---

## 提交

把自查输出的**截图**发到飞书群。

> 截图里要能看到：**仓库地址、分支名、每一行的 ✅/❌、以及最后的结论**。
> 没有结论那一行的截图不算。

---

## 评分

**本作业只有 PASS / FAIL 两个结果。** 下面这些**必须全部通过**
（就是自查输出里的前 11 行）：

- [ ] 存在命名为 `fix/<what>` 等合规格式的任务分支
- [ ] 分支上有实质提交（不是空分支）
- [ ] 所有 commit message 符合 `type(scope): subject`
      （type ∈ `feat` `fix` `refactor` `docs` `test` `chore` `tune` `style`）
- [ ] 没有任何 commit message 属于低信息量黑名单（`update` / `modify` / `tmp` / `改` …）
- [ ] 历史中没有构建产物（`build/` / `*.o` / Keil 生成文件）
- [ ] 工作区与历史中没有冲突标记残留（`<<<<<<<` / `>>>>>>>`）
- [ ] `tests/` 下的测试文件**没有被修改**（改测试让它通过 = 任务没完成）
- [ ] 合并后 `CALIBRATE` 和 `DROP_MODE` 两个枚举值**都存在**
- [ ] 三个 TODO 都已处理
- [ ] 历史里有 **merge commit**（合并确实发生过）
- [ ] `test_encoder` 与 `test_clamp` **全部通过**

**提示项（不影响结论）：**

- 你自己加的提交数超过 15 个
- 某条 message 长度不在 10–72 字符
- 某个 commit 一次跨了太多模块
- 工作区还有未提交的改动
- 任务分支还没推送

> **你 HW1–HW4 的提交也会被一起检查。** 如果那时候写过 `update` 这种 message，
> 这里会挂——回去改好（`git rebase -i` 改写，或者补一条说明性的新提交）。

---

## 常见错误

| 症状 | 原因 | 怎么办 |
| --- | --- | --- |
| `git push` 报 `Permission denied (publickey)` | SSH key 没配好 | 回 Day 0 课件的 PreClass 章节 |
| `git push` 报 `rejected` / `fetch first` | 远端有你本地没有的提交 | `git pull` 之后再 push。**不要用 `--force`** |
| `git status` 里看不到 Keil 那几个文件 | 已经加进 `.gitignore` 了 | 正常，Task 6 的目标就是这个 |
| `git merge upstream/drop-mode` 说 no such ref | 没 `git fetch upstream` | 先 fetch |
| 合并后编译不过 | 冲突标记没删干净 | `git diff` 搜 `<<<<<<<` |
| `test_clamp` 挂了 | 阻力判断改坏了 | 检查 `is_calibrating_` 默认值，别把正常路径也挡掉 |
| 四个改动混成一个提交了 | 提交前用了 `git add .` | `git reset --soft HEAD~1`，然后按 Task 7 分开 add |
| 分支名不符合格式 | 用了中文或大写 | `git branch -m fix/<新名字>` 改名 |
| `python` 命令找不到 | Windows 上没勾 Add to PATH | 用 `py` 代替 `python` |

---

## 参考

| 内容 | 在哪 |
| --- | --- |
| Git 课件（`status` / `diff` / `add` / `commit`） | Day 0 课件 Loop 1–2 |
| 分支与 HEAD | Day 0 课件 Loop 3 |
| 远端与同步 | Day 0 课件 Loop 4 |
| 合并与冲突 | Day 0 课件 Loop 5 |
| Commit message 与分支名的写法 | Day 0 课件「书写约定」一节 |
| 撤销与恢复 | Day 0 课件 Loop 6 |
| 完整的命令速查 | Day 0 课件附录 C |

---

## 卡住了怎么办

1. **先跑 `git status`**，把它输出的原文看一遍——大部分问题它会直接告诉你
2. **再跑 `git log --oneline --graph -8`**，看看自己现在在哪
3. 翻上面的「常见错误」
4. 还不行就带着**这两条命令的输出**去问，不要只说"我 Git 坏了"

---

## 做完之后

回头看一遍你的 `git log`：

```text
feat(arm): add CALIBRATE mode for the calibration flow
fix(clamp): skip resistance check while calibrating
tune(clamp): raise default clamp speed by 1.5x
chore(gitignore): ignore Keil generated files and build output
...
```

**四条提交，每一条只说一件事，每一条半年后你都看得懂。**
这就是这门课想让你养成的习惯。

下一步（HW6）是把这套流程再往前推一步：**发一个 PR，让别人 review 你的改动。**
