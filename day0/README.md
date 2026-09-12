# Day 0 · 先导课

这一天不是六节独立的课，是**一条工具链 + 一条作业链**。

---

## 这一天覆盖什么

| 模块 | 形式 | 说明 |
| --- | --- | --- |
| 环境安装 | **线下** | 装 Keil + CLion + 工具链 + Git，助教巡场逐个过 |
| Git | **线下** | 手把手敲命令，看效果 |
| Keil STM32 全家桶 | 录播 | 工程结构 / 编译下载调试 / 生成文件 |
| CLion 基本环境配置 | 录播 | 工具链 / CMake / 调试配置 |
| clang-format | 录播 | 配置 + 挂到 CLion |
| C++ 基础 | 自学资料 | 不占课时。讲义 + `cpp1`–`cpp4` 四份练习，**独立成一条线** |

---

## 作业链

**所有作业都在同一个工程 [`project/`](project/) 上做。** 这是刻意的——

> 你要先**改 C++ 代码**（HW1–HW4），才**有东西可以 commit**（HW5）。
> Git 作业的提交对象，就是你自己改的代码，不是老师编的假数据。

**两套是独立的，可以在不同时间做：**

| 线 | 编号 | 工程在哪 | 内容 |
| --- | --- | --- | --- |
| **Git 线** | `HW1`–`HW5` | [`project/`](project/) | 构建 → 修 bug → 链接错误 → 格式化 → 用 Git 提交 |
| **C++ 线** | `cpp1`–`cpp4` | [`cpp/`](cpp/) | 声明与定义 → 函数与参数 → 枚举与指针 → 位运算与 CAN 打包 |

### Git 线（HW1–HW5）

| 作业 | 标题 | 配什么 | 状态 |
| --- | --- | --- | --- |
| **HW0** | **环境自检** | 线下当堂 | **[已就绪](homework/hw0-env.md)**（不计分） |
| **HW1** | **把项目跑起来** | CLion / Keil 录播 | **[已就绪](homework/hw1-build.md)** |
| **HW2** | **修编码器回绕** | C++ 自学 + 录播 | **[已就绪](homework/hw2-encoder.md)** |
| **HW3** | **编译与链接** | Keil 录播 | **[已就绪](homework/hw3-link.md)** |
| **HW4** | **格式化** | clang-format 录播 | **[已就绪](homework/hw4-format.md)** |
| **HW5** | **Git 工作流** | **线下 Git 课件** | **[已就绪](homework/hw5-git.md)** |
| **HW6** | **发一个 PR** | Day 0 Git 课件 Loop 4 | **[已就绪](homework/hw6-pr.md)**（不计分，交 PR 链接） |

### C++ 线（cpp1–cpp4）

| 练习 | 标题 | 改哪个文件 | 状态 |
| --- | --- | --- | --- |
| **cpp1** | **声明与定义** | `cpp/base/common/math.cpp` | **[已就绪](homework/cpp1-decl-def.md)** |
| **cpp2** | **函数与参数传递** | `cpp/base/motor/motor.cpp` | **[已就绪](homework/cpp2-functions.md)** |
| **cpp3** | **枚举、switch 与指针** | `cpp/app/chassis.cpp` | **[已就绪](homework/cpp3-enum-pointer.md)** |
| **cpp4** | **位运算与 CAN 打包** | `cpp/base/motor/dji_motor_driver.cpp` | **[已就绪](homework/cpp4-bitops.md)** |

> **C++ 线要先读讲义**（[`cpp/lecture.md`](cpp/lecture.md)，两万多字）。
> 每份练习的任务书里写了该读哪几节。
>
> **两套的自查命令是同一条**：`python tools/grade.py <编号> .`
> 学生和老师跑的是同一份代码。

**建议节奏**（2–3 周）：

```text
第一周   HW0（课上）→ HW1 → HW2          同时：读讲义 A 段 → cpp1
第二周   HW3 → HW4                        同时：讲义 B/C 段 → cpp2 → cpp3
第三周   HW5 → HW6                        同时：讲义 §6c 全部（重点 §6c.5–6）→ cpp4
```

两条线可以并行，但**别把 cpp 线拖到最后** —— `cpp1` 撞的那条
`undefined reference` 和 HW3 是同一个东西，一起做印象更深。

> **先做 HW1 再来做 HW5。** HW5 的「开始之前」清单里要求你已经能构建成功——
> 不然你会分不清"是我的 Git 用错了"还是"我的环境没配好"。

---

## 目录

```text
day0/
├── README.md            你正在看的这份
├── project/             ★ Git 线用的 C++ 工程（HW1–HW5 共用）
├── cpp/                 ★ C++ 线：练习工程 + 讲义
│   ├── README.md        怎么构建、怎么自查
│   ├── lecture.md       自学讲义
│   └── base/ app/ tests/
└── homework/            任务书
    ├── hw1-build.md     把项目跑起来
    ├── hw2-encoder.md   修编码器回绕
    ├── hw3-link.md      编译与链接
    ├── hw4-format.md    格式化
    ├── hw5-git.md       Git 工作流
    ├── cpp1-decl-def.md     声明与定义
    ├── cpp2-functions.md    函数与参数传递
    ├── cpp3-enum-pointer.md 枚举、switch 与指针
    └── cpp4-bitops.md       位运算与 CAN 打包
```

---

## 做完之后

你会得到一份**自己能讲清楚**的提交历史：为什么开分支、为什么分两次提交、
冲突是怎么解决的、合并之后为什么还要重新跑测试。

这些东西以后在真实的战队仓库里每天都会用到。

---

## 学员名单

线下 Git 课「跟做」环节会让你在这里加一行，然后提交上去。
**这是你的第一个 commit** —— 写错也能改，不用紧张。

| 姓名 | GitHub |
| --- | --- |
