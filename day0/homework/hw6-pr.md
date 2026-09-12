# HW6 · 发一个 Pull Request

HW5 你学会了在**自己的仓库**里开分支、合并、解决冲突。
但整个 HW1–HW5 你都只在**自己那一份**里工作 —— 老师的仓库从来没被你的改动碰到过。

这一份就是最后一步：**把你的改动送回课程仓库。**

> **为什么这一步值得单独做一次**
>
> PR 是战队里所有改动的入口。真实仓库有几十个人在推代码，
> 一个 `arm.h` 的改动要过 review 才能进 `main`。
> 你今天要走的这条路（开分支 → 推 → 发 PR → 被 review → 改 → 合入），
> 就是以后每一次改代码走的路。
>
> **这条路走一遍，比读十遍流程图有用。** 尤其是"被 review 之后怎么改"那一段 ——
> 那是新手最容易搞砸的地方（常见做法是关掉 PR 重开一个，于是评论区全丢了）。

---

## 学习目标

1. 分清 **fork 上的分支** 和 **上游仓库的分支** —— 为什么你推的分支出现在你自己的仓库里
2. 学会写 PR 描述：**What / Why / Test / Risk** 四栏，Test 必须诚实
3. 体验 **review 回环**：收到意见后**在原分支继续改**，PR 自动更新，不重开
4. 知道 PR 合入前要确认什么（CI / 自查 / 别人的分支有没有动过同一个文件）

---

## 开始之前

- [ ] 完成了 HW5，`python tools/grade.py hw5 .` 是 PASS
- [ ] `git status` 工作区干净
- [ ] 你配好了 `upstream` 远端（`git remote -v` 里能看到它）

> **`upstream` 没配？** 在仓库根目录执行一次：
>
> ```bash
> git remote add upstream git@github.com:SJTU-RoboMaster-Team/EC-Training-Labs.git
> git remote -v          # 确认 origin（你的）和 upstream（老师的）都在
> ```

---

## 任务

### Task 1 · 从最新的上游开分支

你 fork 出来的那份**不会自动跟着老师更新**。开新分支之前先把上游的改动取下来：

```bash
git fetch upstream
git switch -c feat/your-name-hw6 upstream/main
```

把 `your-name` 换成你的拼音或 GitHub 用户名 —— 分支名要让人一眼看出是谁的、做什么的。

> **为什么从 `upstream/main` 开，不从你本地的 `main` 开？**
>
> 你本地的 `main` 可能已经落后了。从落后的点开分支，
> 你的 PR 里会混进一堆"别人早就合进去的改动"，diff 变得没法看。
> 这是第一次发 PR 最常见的问题。

自查：

```bash
git log --oneline -3
```

应该看到最新的提交来自上游（不是你 HW5 的那几条）。

---

### Task 2 · 挑一个真问题，做一个小改动

去仓库里找一处**真实存在的小问题**，改掉它。要求只有两条：

- **改动小** —— 一个 PR 只做一件事。三五个文件的同一个主题可以，二十个文件换个行不行。
- **真的对** —— 不是"为了交作业随便改一行"。改错了 review 会打回来，那也没关系，正好体验回环。

给几个方向（也可以自己想）：

| 方向 | 例子 |
| --- | --- |
| 文档里的错别字 / 说不清的一句话 | 某份任务书里一个命令写错了 |
| 讲义里对不上的引用 | `lecture.md` 里提到的文件路径/行号变了 |
| 代码里的一个 TODO | `day0/cpp/` 或 `day0/project/` 里剩下的 TODO 注释 |
| 一段可以更清楚的注释 | 某个函数没说清它为什么这么写 |
| `.gitignore` 少了一条 | 你 HW5 里踩过的那个坑 |

> **不建议**：改 grader（`tools/` 下的东西）。那是所有作业共用的尺子，
> 动它要单独讨论，不适合当第一个 PR。

---

### Task 3 · 提交、推到你的 fork

```bash
git add <你改的文件>
git commit -m "docs(hw2): 把 encoder 回绕那句解释改清楚"
git push -u origin feat/your-name-hw6
```

`-u` 只需要第一次带。推完之后 GitHub 的输出里会给你一条**开 PR 的链接**：
`https://github.com/<你>/EC-Training-Labs/pull/new/feat/your-name-hw6`

commit message 的规矩和 HW1–HW5 一样（`type(scope): subject`）。

---

### Task 4 · 发 PR

打开上面那条链接，或者去 GitHub 页面上点 **Compare & pull request**。

**关键：确认 base 仓库是老师的，不是你的。**

| 栏位 | 应该是什么 |
| --- | --- |
| **base repository** | `SJTU-RoboMaster-Team/EC-Training-Labs` |
| **base** | `main` |
| **head repository** | `<你的用户名>/EC-Training-Labs` |
| **compare** | `feat/your-name-hw6` |

> 如果 base 显示的是你自己的仓库，说明你在自己仓库的页面上点了 Pull Request ——
> 那是"把 A 分支合进 B 分支"，不是发给老师。回到课程仓库页面重新点。

PR 标题用你那条 commit 的主旨，描述按模板填四栏：

```markdown
## What
改了什么。（一句话说清，不要"优化了一些代码"。）

## Why
为什么要改。哪里不对、谁会被它坑到。

## Test
**你怎么确认改对了。** 诚实地写：
- 改了命令 → 把命令跑一遍，贴上输出
- 改了文档 → 说明你按新文档走了一遍没卡住
- 只改了错别字 → 写"纯文字改动，未运行代码"也行

**"我只在仿真里试过"和"上车实测通过"是完全不同的结论。** 写清楚是哪种。

## Risk
已知的风险或没做的事。没有就写"无"。
```

---

### Task 5 · 收到 review 之后

老师或助教会留评论。**这是这份作业最重要的一步。**

正确的做法：

```bash
# 还在同一个分支上
git add <改的文件>
git commit -m "docs(hw2): 按 review 意见补充回绕的取值例子"
git push
```

**就这两条命令。** PR 会自动带上新提交，评论区完整保留。

> **不要这么做**
>
> | 错误做法 | 后果 |
> | --- | --- |
> | 关掉 PR 重新开一个 | 之前的讨论全丢，reviewer 要重新看一遍 |
> | `git push --force` 把历史重写掉 | reviewer 的评论指向的代码行对不上了 |
> | 新建一个分支重新提交 | 同上，而且 PR 里看不出这是同一件事 |
> | `git commit --amend` 后强推 | 除非 reviewer 明确让你把提交压成一个，否则别做 |

如果 reviewer 明确说"把这两个提交压成一个"，再按他说的做（`git rebase -i` + 强推，
并且**在 PR 里说一句已经改好了**）。

---

### Task 6 · 合入之后收尾

PR 被合入（merge）之后：

```bash
git switch main
git fetch upstream
git merge upstream/main          # 或者 git pull upstream main
git branch -d feat/your-name-hw6 # 本地分支删掉
```

顺手把远端那个分支也删掉 —— GitHub 在 PR 合入后会给一个 **Delete branch** 按钮。
一个已经合入的分支留着，只会让下次 `git branch -a` 更难读。

---

## 提交什么

**这份作业不看 `grade.py`，交的是 PR 链接。**

把 PR 链接发到飞书群，格式：

```text
HW6 · <你的名字> · https://github.com/SJTU-RoboMaster-Team/EC-Training-Labs/pull/<编号>
```

> **为什么没有 `python tools/grade.py hw6 .`？**
>
> PR 在 GitHub 上，`grade.py` 是在你本地跑的一个程序 —— 它看不到 PR，
> 也看不到 review 评论。硬做一个"检查 PR"的规则，只能靠 GitHub API 和 token，
> 那就不是"学生本地自查"了。
>
> 所以这一份的验收是**人看**：老师和助教在 PR 页面上看四件事 ——
> diff 是不是一件事、描述四栏填没填、Test 那一栏诚不诚实、review 之后改得对不对。
>
> 这一份**不计分**。但下一赛季真正推代码的时候，走的就是这条路。

---

## 评分

**不计分。** 验收方式是人看 PR，看四件事：

- [ ] PR 的 base 是 `SJTU-RoboMaster-Team/EC-Training-Labs`，不是自己的 fork
- [ ] diff 只做了一件事，改动范围说得清
- [ ] 描述里有 What / Why / Test / Risk 四栏，**Test 一栏写了真实做过什么**
- [ ] 收到 review 意见后，是**在原分支继续提交**的（评论区能看到这个回环）

---

## 常见错误

| 症状 | 原因 | 怎么办 |
| --- | --- | --- |
| PR 里混进了几十个别人的提交 | 从自己落后的 `main` 开的分支 | 改用 `git switch -c <分支> upstream/main` 重开 |
| 页面上找不到 Compare & pull request | 分支没推上去 | `git push -u origin <分支>`，然后回仓库首页看 |
| base 显示成我自己的仓库 | 在自己 fork 的页面点了 PR | 回到课程仓库页面重新点（base 要在左边） |
| PR 显示 "There isn't anything to compare" | base 和 compare 选了同一个分支 | compare 选你的 `feat/...` 分支 |
| 推上去要输密码 | 用的是 HTTPS 地址 | 换 SSH（`git remote set-url origin git@github.com:...`） |
| review 之后不知道怎么办 | 以为要重开 PR | 在原分支 `git add` + `git commit` + `git push`，PR 自己会更新 |
| PR 里有冲突提示 | 上游在你开分支之后又动了同一个文件 | 本地 `git fetch upstream && git merge upstream/main`，解完冲突再 push |

---

## 参考

| 内容 | 在哪 |
| --- | --- |
| PR 的完整流程与最小模板 | **Day 0 Git 课件 Loop 4** |
| `origin` / `upstream` 分别是什么 | Day 0 Git 课件 Loop 4「origin/main 是什么」 |
| 分支命名与生命周期 | Day 0 Git 课件 Loop 3 |
| 冲突怎么解 | **HW5 Task 9–10**，或 Day 0 Git 课件 Loop 5 |
| 撤销与恢复 | Day 0 Git 课件 Loop 6 |
| `fetch` / `pull` / `push` 的分工 | Day 0 Git 课件 Loop 4 |

---

## 做完之后

**Git 线到这里就结束了。** 你现在会的东西：

- 把一个工程从零构建起来，看懂编译器和链接器在抱怨什么
- 用 `git status` / `git diff` 看清自己改了什么，再决定怎么提交
- 在分支上工作，把不相关的改动拆成多个 atomic commit
- 同步上游、解决真实冲突、重新验证
- 走完一次 PR：发出去、被 review、按意见改、合入

**这些是后面所有模块的地基。** 接下来不管是 CAN 通信、电机控制还是整车调试，
每一份代码都要经过今天走的这条流程才能进 `main`。
