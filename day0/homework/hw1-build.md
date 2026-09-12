# HW1 · 把项目跑起来

这是 Day 0 作业链的第一份。目标只有一个：**让这个工程在你自己机器上编译起来、跑出测试结果。**

看起来简单，但它是后面四份作业的地基——**跑不起来，后面全部做不了**。

---

## 学习目标

1. 会用 **CLion** 或**命令行**打开一个 CMake 工程并构建它
2. 能跑出测试结果，并**看懂哪几个通过了、哪几个没通过**
3. 理解"测试现在有一个失败"是**正常的**——那是 HW2 要修的东西

---

## 开始之前

- [ ] 完成了 Day 0 课上的环境安装（CLion / 工具链 / Git）
- [ ] `python --version` 有输出（Windows 上是 `python`，WSL/Linux 上可能是 `python3`）
- [ ] `cmake --version` 有输出
- [ ] 已经 Fork 了这个仓库，并 clone 到了本地

---

## 获取代码

```bash
git clone git@github.com:<你的用户名>/EC-Training-Labs.git
cd EC-Training-Labs/day0/project
```

> ⚠️ **工作目录：后面所有命令都在 `day0/project/` 里执行。**

---

## 任务

### Task 1 · 先看一眼这个工程长什么样

```text
day0/project/
├── CMakeLists.txt        构建配置
├── app/                  业务模块
│   ├── arm.h             共享类型（枚举、结构体）
│   ├── control.*         调度入口
│   ├── motor_monitor.*   电机反馈
│   └── clamp.*           夹爪
├── base/
│   ├── motor.h           电机数据结构
│   └── math.h            数学工具
├── tests/                单元测试
└── tools/
    ├── build.py          一键构建 + 测试
    └── make_generated_files.py （HW5 才用，现在不用管）
```

**怎么验证：** 你能说出"电机反馈"的代码在哪个文件里。

---

### Task 2 · 构建 + 跑测试

**两条路，选一条。CLion 更省事，命令行更能看清发生了什么。**

#### 路线 A · CLion（推荐）

1. CLion → **File → Open**，选中 `day0/project` 这个**目录**（不是单个文件）
2. 等右下角进度条跑完（CLion 会自动配置 CMake）
3. 顶部工具栏的构建目标选 **All CTest** 或 **All targets**，点 🔨 构建
4. 构建完，在左下角 **Run** 面板里应该能看到 `test_encoder` / `test_clamp` 两个目标

> **第一次打开可能会问工具链**。选 CLion 自带的 **MinGW** 或 **Visual Studio** 都行。
> 如果提示找不到编译器，看 Day 0 课件的环境配置一节。

#### 路线 B · 命令行

```bash
python tools/build.py
```

**你应该看到：**

```text
============================================================
配置 (cmake configure)
============================================================
$ cmake -S . -B build -DCMAKE_BUILD_TYPE=Debug
...
============================================================
构建 (cmake build)
============================================================
...
============================================================
测试 (ctest)
============================================================
    Start 1: encoder
1/2 Test #1: encoder ..........................***Failed    0.00 sec
  [ ok ] plain forward                got    10.00
  [ ok ] plain backward               got   -10.00
  [FAIL] forward across zero          got  -348.00  want    12.00
  [ ok ] backward across zero         got   -12.00
test_encoder: 3/4 passed

    Start 2: clamp
2/2 Test #2: clamp ............................   Passed    0.00 sec

50% tests passed, 1 tests failed out of 2
```

**怎么验证：**

- [ ] 构建成功（没有编译错误）
- [ ] `test_clamp` **通过**
- [ ] `test_encoder` **失败 1 个用例**（`forward across zero`）

> ### ⚠️ 现在这个失败是**对的**
>
> `test_encoder` 失败**不是你的环境有问题**，是工程里**本来就有一个 bug**。
> HW2 会带你把修好。**这一份作业不要动任何代码。**

---

### Task 3 · 看清失败的那一个用例

打开 `tests/test_encoder.cpp`，找到这四行：

```cpp
const float fwd[] = {10.0f, 15.0f, 20.0f};
testutil::check_near("plain forward", run(fwd, 3), 10.0f, 0.01f);

const float back[] = {20.0f, 15.0f, 10.0f};
testutil::check_near("plain backward", run(back, 3), -10.0f, 0.01f);

const float fwd_wrap[] = {355.0f, 359.0f, 3.0f, 7.0f};
testutil::check_near("forward across zero", run(fwd_wrap, 4), 12.0f, 0.01f);   // ← 这个挂了

const float back_wrap[] = {5.0f, 1.0f, 357.0f, 353.0f};
testutil::check_near("backward across zero", run(back_wrap, 4), -12.0f, 0.01f);
```

**怎么验证：** 你能回答——**四个用例里挂了几个？挂的是哪一个？**

> 💡 **记住这个问题。** 为什么四个里只挂一个，是 HW2 的关键线索。

---

## 自查

```bash
# 在你仓库的根目录下（就是 EC-Training-Labs/ 这一层）
python tools/grade.py hw1 .
```

> **`grade.py` 就在你的仓库里**（`tools/grade.py`）。它和老师用的是同一份代码，
> 所以**你跑出什么结果，老师就验收什么结果**。

**期望看到：**

```text
┌────────────────────────────────────────────────────────────┐
│ HW1 · 把项目跑起来                                         │
├────────────────────────────────────────────────────────────┤
│ ✅ 能构建                 cmake 配置 + 编译通过            │
│ ⚠️ 工作区干净             没有未提交的改动                 │
├────────────────────────────────────────────────────────────┤
│ 结论   PASS                                                │
└────────────────────────────────────────────────────────────┘
```

> 这一份作业**没有任何 commit**——你只是把项目跑起来看看。
> 所以"工作区干净"是提示项，不影响结论。

---

## 提交

把**构建成功的输出**和**测试结果**截图发到飞书群。

截图里要能看到：
- `test_clamp` 通过
- `test_encoder: 3/4 passed`（**有一个失败是对的**）

---

## 评分

**只有 PASS / FAIL。**

- [ ] 工程能配置（cmake configure 成功）
- [ ] 工程能编译（没有编译错误）
- [ ] 工作区干净（构建产物不该出现在 `git status` 里）

提示项（不影响结论）：
- 你自己加的提交数（超过 15 个会提示）

---

## 常见错误

| 症状 | 原因 | 怎么办 |
| --- | --- | --- |
| `cmake: command not found` | cmake 没装或不在 PATH | 用 CLion 自带的；或回 Day 0 环境配置 |
| `No CMAKE_CXX_COMPILER could be found` | 没装编译器 | CLion → Settings → Build → Toolchains，选 MinGW 或 VS |
| CLion 打开后一片红 | 打开的是文件不是目录 | **File → Open** 选 `day0/project` 目录 |
| `python: command not found` | Windows 上没装 Python 或没勾 Add to PATH | 重装 Python 时勾上；或用 `py` 代替 `python` |
| 构建报中文乱码 | Windows 终端编码 | 用 CLion 的构建窗口看，或 `chcp 65001` |
| `test_encoder` 全过了 | **不可能**，除非你改了代码 | 你确定没动过 `base/math.h`？ |

---

## 参考

| 内容 | 在哪 |
| --- | --- |
| CLion 基本操作 | Day 0 录播 · `Tools/02-clion-setup.md` |
| 编译与链接 | Day 0 录播 · `Tools/01-keil-stm32.md` |
| CMake 是什么 | 同上 |

---

## 做完之后

你现在有一个**能编译、能跑测试**的工程。记住 `test_encoder` 挂了 1 个用例——
下一份作业就是修它。
