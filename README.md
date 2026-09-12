# EC Training Labs

上海交通大学 · 交龙战队 · RoboMaster 电控组 —— **培训作业仓库**。

这里放的是培训期间要动手做的东西。**不要只读代码**，作业是要你在上面改、提交、推上来的。

---

## 怎么用

**学生：**

```text
1. Fork 这个仓库到你自己的 GitHub 账号（保持 public）
2. git clone git@github.com:<你的用户名>/EC-Training-Labs.git
3. 打开对应那一天的 README，从「开始之前」往下做
```

> 保持 public 是必须的——验收工具靠 `git clone` 拿仓库，私有仓库没法验收。

**内容按天组织：**

| 目录 | 内容 |
| --- | --- |
| [`day0/`](day0/) | 先导课：环境、Keil、CLion、Git、clang-format、C++ |
| [`day0/homework/`](day0/homework/) | 全部任务书（两套：`hw*` 和 `cpp*`） |

以后会有 `day1/`、`day2/`……

---

## 仓库结构约定

```text
EC-Training-Labs/
├── README.md            你正在看的这份
├── tools/               自查 / 验收工具
└── day0/
    ├── README.md        这一天怎么走：有哪些练习、按什么顺序
    ├── project/         Git 线用的代码工程（HW1–HW5）
    ├── cpp/             C++ 线：练习工程 + 讲义
    └── homework/        ★ 全部任务书
└── (day1/ …)
```

**两条线，两个工程：**

| 线 | 编号 | 工程 | 做什么 |
| --- | --- | --- | --- |
| Git 线 | `HW1`–`HW5` | `day0/project/` | 构建 → 修 bug → 链接错误 → 格式化 → **用 Git 提交** |
| C++ 线 | `cpp1`–`cpp4` | `day0/cpp/` | 声明与定义 → 函数 → 枚举与指针 → 位运算 |

**为什么 Git 那份不单独建仓库**：它的作业是**一条链**，都在同一个工程上做 ——
先能编译、再修 bug、再格式化、最后把这些改动**有组织地提交上去**。
分开建仓库的话，Git 那份就只能提交老师编的假数据了。

**C++ 线为什么要独立**：它练的是语言和固件常识，和"用 Git 交作业"是两件事。
混在一起的话，一边改错会搅乱另一边的验收。

**两条线的自查命令是同一条**（在仓库根目录下）：

```bash
python tools/grade.py hw3 .      # Git 线
python tools/grade.py cpp1 .     # C++ 线
python tools/grade.py --list     # 看全部
```

---

## 遇到问题

1. 先看那份作业任务书里的**「常见错误」**一节
2. 再跑 `git status`，把它输出的原文看一遍
3. 还不行，带着 `git status` 和 `git log --oneline --graph -8` 的输出去问
