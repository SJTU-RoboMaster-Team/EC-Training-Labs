# C++ 基础 · 自学讲义
<!-- ⚠️ 这个文件由 lab/sync_grader.py 从 CppBasics/raw-source.md 复制而来。
     要改请改那份，然后重新同步 —— 不要直接改这里。 -->

> RoboMaster 电控组 · 27 赛季 Day 0
> 文中的命令输出都是在本机（g++ 11.4.0 / cmake 3.22.1）实际跑出来的，见附录 A。

## 这份讲义里的代码从哪来

**两类，格式不一样，看引用就能分辨：**

| 引用格式 | 来源 | 你该怎么读 |
| --- | --- | --- |
| `base/common/math.h:25` | **练习工程** `day0/cpp/`（HW 里你要动手改的那份） | 这些是你马上要用的 |
| `wheel-legged/base/common/math.cpp:157` | **战队真实仓库**（下面是哪两个） | 这些是"以后你每天看到的东西" |

真实仓库：

| 简称 | 仓库 | 本文引用的提交 |
| --- | --- | --- |
| `wheel-legged` | `SJTU-RoboMaster-Team/Wheel-Legged-Robot-2026` | `04d1227`（`master`） |
| `dual-arm` | `SJTU-RoboMaster-Team/RM2026-Dual-Arm-Engineer` | `ef71f78`（`EngineerDeltA_Main`） |

两个仓库都是 private。看不了也没关系 —— 讲义里把该看的那几段**原样抄下来了**，
你理解它们不依赖能不能打开仓库。

> **为什么引用要带提交号**：真实代码会改。带上提交号，这份讲义里的行号
> 三年后还能对得上。整个模块的选材依据（每个知识点在真实代码里出现多少次）
> 见 `SYLLABUS.md`。

---

## 0. 这份文档怎么用

### 0.1 它是什么

C++ 基础在 Day 0 **不占课时、不线下讲**。它是发给你的自学资料。

定位很具体：你**已经会 C 或者写过一点 C++**（知道变量、`for`、函数、指针），
但你**没在真实工程里用过现代 C++**。所以这份讲义不讲语法入门，只讲一件事：

> 在这个机器人工程的代码里，你会**读到**和**写到**的那些 C++ 用法。

每讲一个知识点，后面都会跟一段「工程里在哪见过它」，指出真实文件和行号。
看到那种段落，**一定要把那个文件打开看一眼**。光看讲义不打开代码，等于没学。

### 0.2 学完你应该能做到

1. 打开 `day0/project` 里任何一个文件，能说出它是什么角色、为什么这么写；
2. 看到 `undefined reference`，知道这是链接阶段的问题，并且知道去哪找（HW3）；
3. 自己要加一个函数、一个常量、一个模块时，知道该放头文件还是放 `.cpp`；
4. 知道这个工程为什么**一处 `new`、一处 `try`、一个 `std::vector` 都没有**。

### 0.3 建议路径与时间

按顺序读，不要跳。**五段加起来大约 5 小时**（只算读，不算动手做练习）：

| 段 | 章节 | 内容 | 时间 |
| --- | --- | --- | --- |
| A | §1–§3 | 工程结构、头文件、**声明 vs 定义** | 60 min |
| B | §4–§6 | `inline` 与 ODR、`const`/`constexpr`、引用 | 50 min |
| **B2** | **§6b–§6c** | **指针 · 位运算与类型转换** | **45 min** |
| C | §7–§10 | 类与函数、`enum class`、命名空间、`static` | 85 min |
| D | §11–§14 | 编译单元与链接、模板、嵌入式约束、`std::`、`extern "C"` | 65 min |
| — | §16–§17 | 自测题 + 答案（可最后做） | 20 min |

> **B2 段别跳。** 练习 `cpp4` 整份都建立在它上面，`cpp1` 也要用 §6c.3–§6c.4。
> 它原来是漏的 —— 补上之前，两份练习要求的章节在路径里没有位置。

**「如果你只有 30 分钟」**：读 §3（声明与定义）、§6c.1（位运算）、§7b.2（参数怎么传），
再扫一眼 §0.4 的对应表。这三节能解释你在练习里会撞到的绝大部分报错。详细版在 `README.md`。

### 0.4 和作业的对应

C++ 模块的练习在 **`day0/cpp/`** 这个工程里，编号 `cpp1`–`cpp4`：

| 练习 | 你要做的事 | 先读哪些节 |
| --- | --- | --- |
| `cpp1` 声明与定义 | 实现 `base/common/math.cpp` 里的四个函数 | **§3**、§4、§6.7、§6c.1–§6c.4 |
| `cpp2` 函数与参数传递 | `Motor::setTorque` —— **先限幅、再转整数** | **§7b.1–§7b.3**、§6c.3 |
| `cpp3` 枚举、switch 与指针 | 状态机 `Chassis::update` + `modeName` | **§8.1–§8.3**、§6b |
| `cpp4` 位运算与 CAN 打包 | 解析 / 打包 C620 报文 | **§6c 全部**（重点 §6c.5、§6c.6） |

> 这张表是**唯一权威**。`README.md`、课件、四份任务书里的「先读哪几节」都照它。
> （曾经五处各写一份，其中三处没给 `cpp1` 列 §6c —— 结果是照着别处的表读，
> 打开 `math.cpp` 会发现有个函数你完全没读到过。）

`cpp1` 做完你会发现工程从"链接不过"变成"能跑"——那正是 §3.5 讲的那条报错。

**另一条线是 Git 模块的 HW1–HW5**（在 `day0/project/` 里）。两套是独立的，
但概念是同一批，碰到了可以对照看：

| 作业 | 你会做的事 | 相关节 |
| --- | --- | --- |
| HW2 | 修 `base/math.h` 里的回绕 bug | §6.7（真实仓库的同一段）、§5.4 |
| HW3 | 制造并修复一个链接错误 | §3.5、§11.2、§11.3 |
| HW5 | 提交改动、处理冲突 | §8.4（枚举追加点）、§10 |

§3.5 是 HW3 的直接答案。**先自己把 HW3 做一遍再回来看**，效果差很多。

### 0.5 自测怎么用

§16 有 20 道题，答案在 §17，**分开的**。做完再对答案，对完把错的题回到对应小节重读。

---

## 1. 先看清这个工程

### 1.1 目录与职责

```text
day0/project/
├── CMakeLists.txt        构建配置：哪些 .cpp 参与编译、头文件去哪找
├── app/                  业务模块
│   ├── arm.h             共享类型（枚举、结构体）
│   ├── control.h/.cpp    调度入口
│   ├── motor_monitor.h/.cpp  电机反馈（累计角度）
│   └── clamp.h/.cpp      夹爪状态机
├── base/
│   ├── motor.h           电机数据结构
│   └── math.h            数学工具（只有 inline 函数，没有 .cpp）
├── tests/
│   ├── test_util.h       极简断言
│   ├── test_encoder.cpp  编码器累计角度测试
│   └── test_clamp.cpp    夹爪回归测试
├── tools/
│   ├── build.py          一键配置 + 构建 + 测试
│   └── make_generated_files.py  （HW5 用）
└── mcu/stm32f407/MDK-ARM/day0.uvprojx   Keil 工程
```

注意两个**没有 `.cpp` 的头文件**：`app/arm.h` 和 `base/motor.h`。它们只放类型定义，
不放实现，所以不需要编译单元。`base/math.h` 也是——但原因不同，它把实现写成了 `inline`
（§4.1）。这三种"头文件"的区别是这份讲义的第一条主线。

### 1.2 一次构建发生了什么

`python tools/build.py` 打印三段（`tools/build.py:141`、`:149`、`:160`）：配置 → 构建 → 测试。

真正的构建命令是 `cmake --build build`，它对每个 `.cpp` 做四步：

```text
motor_monitor.cpp
  ① 预处理  把 #include 的头文件内容原样贴进来、展开宏      → 预处理后的 .ii
  ② 编译    语法检查、类型检查、生成汇编                    → .s
  ③ 汇编    汇编变机器码                                   → .o（目标文件）
  ④ 链接    把所有 .o 和库拼成一个可执行文件，解析符号引用   → test_encoder
```

①②③ 是**逐文件**做的，各文件之间互不知情；④ 是**全局**做的，只有它能发现
"你调用了一个没实现的函数"。这就是 HW3 那个错误的根源，§3.5 展开。

### 1.3 编译单元（TU）

一个 `.cpp` 加上它 `#include` 进来的所有头文件，预处理之后合成一个大的源码文件，
这个文件叫一个**编译单元**（translation unit，TU）。编译器一次只看得见一个 TU。

工程里 `CMakeLists.txt:11-15` 列出三个 `.cpp`：

```cmake
add_library(day0_core
  app/control.cpp
  app/motor_monitor.cpp
  app/clamp.cpp
)
```

所以这个库有**三个 TU**，加上测试两个，一共五个。库的名字叫 `day0_core`，
产物是 `build/libday0_core.a`（一个静态库，里面装着三个 `.o`）：

```bash
$ ar t build/libday0_core.a
control.cpp.o
motor_monitor.cpp.o
clamp.cpp.o
```

`CMakeLists.txt:16` 这行决定了 `#include` 怎么写：

```cmake
target_include_directories(day0_core PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})
```

它把工程根目录加进头文件搜索路径，所以工程里所有包含都写成**从根目录算起的相对路径**——
`#include "app/arm.h"`、`#include "base/math.h"`，而不是 `#include "../base/math.h"`。
真实的编译命令里能看到这个 `-I`。想自己看一眼的话，CMake 把它写在了
`build/CMakeFiles/day0_core.dir/flags.make`（一个纯文本文件，用编辑器打开就行）。

顺带一句：`CMakeLists.txt:4` 写的是 `set(CMAKE_CXX_STANDARD 17)`，实际传下去是
`-std=gnu++17`（GNU 扩展默认开着）。这两个不是一回事，嵌入式工具链上尤其要注意。

> **工程里在哪见过它**：`CMakeLists.txt:11-16`、`tools/build.py:141-165`、
> `app/control.cpp:1-4`（一个 TU 里包含了自己模块的头 + 两个别的模块的头）。

---

## 2. 头文件与 `#include`

### 2.1 `" "` 和 `< >` 的区别

```cpp
#include "app/arm.h"     // 先在当前文件所在目录找，再找 -I 路径
#include <cstdint>       // 只找系统/工具链的头文件目录
```

工程里两者都用：`app/arm.h:4` 是 `#include <cstdint>`（用 `uint8_t` 就必须包含它），
`app/control.h:4` 是 `#include "app/arm.h"`。

规则不是"引号找自己的、尖括号找系统的"这么死——实现上引号形式多找一些路径。
可移植的写法只有一条：**自己的头文件用引号，标准库和工具链的用尖括号。**

### 2.2 include guard：为什么必须写

头文件会被很多 TU 包含，也可能在同一个 TU 里被间接包含两次。比如 `app/control.cpp`
包含了 `app/control.h`，而 `app/control.h:4` 又包含了 `app/arm.h`；如果同一份文件再被
包含一次，里面的类型就会被定义两遍。

工程里每个头文件都用这种写法（`app/arm.h:1-2`、`base/math.h:1-2`、`tests/test_util.h:1-2`）：

```cpp
#ifndef DAY0_APP_ARM_H
#define DAY0_APP_ARM_H

// ... 内容 ...

#endif  // DAY0_APP_ARM_H
```

宏名字用**路径全大写**（`DAY0_APP_ARM_H`），就是为了不和别的头文件撞名。

把 guard 去掉会怎样？实测（把 `app/arm.h` 的宏去掉，同一次编译里包含两遍）：

```text
noguard.h:2:6: error: multiple definition of 'enum Mode_e'
    2 | enum Mode_e : uint8_t { FOLD, CRUISE };
      |      ^~~~~~
noguard.h:2:6: note: previous definition here
```

这是**编译错误**而不是链接错误——因为问题出在同一个 TU 内部。带上 guard 之后，
`app/arm.h` 这个文件在一次编译里只会被真正打开一次，可以自己验证：

```bash
$ g++ -std=c++17 -I<工程根> -E -H dbl.cpp 2>&1 >/dev/null | head -1
. /home/.../day0/project/app/arm.h
```

### 2.3 `#pragma once`

一行顶上面三行，所有主流编译器（gcc/clang/MSVC/Keil 的 armcc）都支持。
工程里**没有用**它，用的是传统宏写法。两种都行，唯一的要求是**同一个工程里保持一致**。
你新加头文件时，跟着工程现有风格写宏。

### 2.4 头文件里该放什么

工程里的分工很清楚，照着抄就行：

| 放什么 | 例子 | 为什么 |
| --- | --- | --- |
| 类型定义（`struct` / `enum` / `class` 的声明） | `app/arm.h:8`、`app/arm.h:28`、`app/clamp.h:7` | 多个模块都要用同一个类型，得有个共同来源 |
| 函数声明 | `app/control.h:6-8`、`app/motor_monitor.h:9-16` | 告诉别人"有这么个函数可以调" |
| 类的成员函数定义（短小的） | `app/clamp.h:11`、`app/motor_monitor.h:18` | 类体里定义的成员函数隐含 `inline`（§4.5） |
| `inline` 自由函数定义 | `base/math.h:8`、`base/math.h:15` | 见 §4.1 |
| `constexpr` 常量 | `app/arm.h` 里没有，见 `app/control.cpp:10-13` | 常量放头文件才能被多个模块共享 |
| **不该放**：普通函数定义、全局变量定义 | —— | 会在多 TU 里重复定义，报 `multiple definition`（§4.2） |

### 2.5 包含顺序

`clang-format` 的配置里（`.clang-format:23-30`）规定了包含分三类排序：
`<...>` 优先，然后 `"..."`，最后其他。工程里的实际写法（`app/motor_monitor.cpp:1-3`）：

```cpp
#include "app/motor_monitor.h"

#include "base/math.h"
```

第一行是**自己的头文件**，然后用一个空行隔开。这不是强迫症，是一个实用习惯：
自己的头文件先包含，如果它漏写了依赖（比如忘了 `#include <cstdint>`），编译会当场报错，
而不是等到别人包含它的时候才炸——这种错误叫"头文件不自包含"。

> **工程里在哪见过它**：`app/control.h:1-4`、`app/arm.h:1-4`、`base/math.h:1-2`、
> `app/motor_monitor.cpp:1-3`、`.clang-format:23-30`。

---

## 3. 声明与定义（本文主线）

这一节是整份讲义的核心。你在 HW3 里遇到的 `undefined reference`、在头文件里该写什么、
`inline` 为什么存在，全都挂在"声明"和"定义"这对概念上。

### 3.1 两者分别是什么

- **声明**（declaration）：告诉编译器"有这么个东西，它叫什么、什么类型"。
  信息够编译器检查调用写对没有，但不够生成代码。
- **定义**（definition）：给出实体本身。对函数来说是函数体，对变量来说是存储空间，
  对类型来说是完整的成员列表。

对函数来说，区分很简单：**带 `{}` 函数体的就是定义**。

```cpp
void controlInit();                             // 声明
void controlInit() { /* ... */ }                // 定义
```

工程里两种写法都在：`app/control.h:6` 是声明，`app/control.cpp:24` 是定义。

### 3.2 函数的三种写法

**写法 1：头文件声明 + `.cpp` 定义**（最主流）

```cpp
// app/clamp.h:9
void beginCalibration();
```

```cpp
// app/clamp.cpp:3
void Clamp::beginCalibration() {
  is_calibrating_ = true;
  state_ = ClampState::kIdle;
}
```

注意 `.cpp` 里的 `Clamp::`——出了类体，成员函数必须带上类名，否则编译器以为你在定义
一个叫 `beginCalibration` 的自由函数。

**写法 2：头文件里 `inline` 定义**（短小、和类型强相关的工具函数）

```cpp
// base/math.h:15-19
inline float clampf(float v, float lo, float hi) {
  if (v < lo) return lo;
  if (v > hi) return hi;
  return v;
}
```

**写法 3：只有声明，没有定义**（HW3 故意制造的现场）

```cpp
// HW3 里你把 base/math.h 改成这样
float wrap_angle_deg(float deg);
```

写法 3 本身**不违法**：一个函数可以只声明不定义，只要没人调用它，
或者调用它的地方最后能链接到某个定义。链接器的工作就是保证"调用了就得有"。

### 3.3 变量：声明与定义的区别更微妙

```cpp
int g_count;              // 定义：分配了存储空间
extern int g_count;       // 声明：只是告诉编译器别处有一个，不分配
int g_count = 0;          // 定义（带初始化）
```

工程里的全局对象是**定义**（`app/control.cpp:18-20`）：

```cpp
namespace {

MotorMonitor g_joint_monitor;
Clamp g_clamp;
Mode_e g_mode = Mode_e::FOLD;

}  // namespace
```

这三行是定义：它们各自构造了一个对象。它们不会造成重复定义，原因不是"写在 `.cpp` 里"，
而是因为它们处在**匿名命名空间**里，具有内部链接——每个 TU 一份，别人看不见（§9.3）。
这是工程里最重要的一处设计选择：**模块私有的状态放匿名命名空间，共享的类型放头文件。**

### 3.4 类定义可以出现在头文件里，为什么不怕重复

`class Clamp { ... };` 是类型定义，照理说"定义"不该重复。但类定义是例外：
**同一个类在多个 TU 里逐字相同地定义，是合法的**（这是 ODR 的一部分，§4.2）。
不合法的是同一个 TU 里出现两次——那正是缺 include guard 时报的
`multiple definition of 'enum Mode_e'`（§2.2）。

所以：

- 类型（`class` / `struct` / `enum` / `union` / 模板）→ 放头文件，多处出现没关系；
- 函数体、全局变量 → 放 `.cpp`；要放头文件就必须是 `inline` / `constexpr` / 类的成员函数。

### 3.5 HW3 的 `undefined reference` 根因（重点）

HW3 让你把 `base/math.h` 里的 `deg_normalize_180` 实现删掉，只留一行声明，并且把
`app/motor_monitor.cpp:17` 的调用点改成新名字：

```cpp
data_.angle += wrap_angle_deg(raw_angle_deg - data_.last_raw_angle);
```

然后构建。真实结果（本机复现，完整输出见附录 A）：

```text
[ 25%] Building CXX object CMakeFiles/day0_core.dir/app/motor_monitor.cpp.o   ← 编译过了
[ 50%] Linking CXX static library libday0_core.a                              ← 库也建成了
[ 75%] Linking CXX executable test_encoder
/usr/bin/ld: ../libday0_core.a(motor_monitor.cpp.o): in function `MotorMonitor::update(float, float, float)':
app/motor_monitor.cpp:17: undefined reference to `wrap_angle_deg(float)'
collect2: error: ld returned 1 exit status
```

拆开看这几行：

1. **编译 `motor_monitor.cpp` 没有报错。** 编译器只处理这一个 TU。它看到了
   `float wrap_angle_deg(float);` 这行声明，于是知道"这个函数存在，参数是 `float`，
   返回值是 `float`"，调用写对了。至于函数体在哪——**编译器根本不去看别的 `.cpp`**，
   它也无权判断。这也解释了为什么 `void controlInit();` 这种只有声明的写法不会立刻报错。
   （想验证的话：`g++ -std=c++17 -I. -fsyntax-only app/motor_monitor.cpp` 退出码 0。）

2. **`libday0_core.a` 也建成了。** 静态库只是 `.o` 的打包，`ar` 不解析符号，
   它**不关心里面有没有未定义的引用** —— 一个 `.a` 里允许存在「用到了但没定义」的符号。
   所以「库编过了」不等于「没问题」。

3. **报错发生在链接 `test_encoder` 的时候。** 链接器把 `test_encoder.cpp.o`、
   `libday0_core.a` 里的 `.o` 和 C++ 运行库拼在一起，建立符号表。它发现了
   `motor_monitor.cpp.o` 里有个 `U wrap_angle_deg(float)`，但在所有输入里都找不到
   对应的定义（`T`），于是报 `undefined reference`。

**三条结论，记住它们：**

- `undefined reference to ...` = **链接**错误（`ld`），`error: expected ...` = **编译**错误；
- 报错里指出的文件（`motor_monitor.cpp:17`）是**调用点**，不是缺失定义的地方。
  要找的是"谁该定义它"；
- 缺定义有两种修法（HW3 Task 4）：

  | 做法 | 怎么修 | 什么时候用 |
  | --- | --- | --- |
  | A · 新建 `.cpp` | 写 `base/angle.cpp` 定义它，**并加进 `CMakeLists.txt:11-15`** | 实现比较长、要单独测、要减少重编译 |
  | B · 留在头文件 | 写成 `inline float wrap_angle_deg(float deg) { ... }` | 实现短、纯计算、和现有 `base/math.h` 一致 |

  **做法 A 里最容易漏的一步是改 `CMakeLists.txt`。** 文件写了但没加进构建系统，
  症状和"根本没写"一模一样——这是真实工程里最常见的链接错误来源。

修复后再链接一次，那一行 `undefined reference` 就没了 —— 链接器终于找到了定义。

### 3.6 遇到 `undefined reference` 的三步

1. 看报错里的**符号名**（`wrap_angle_deg(float)`）和**调用点**（`motor_monitor.cpp:17`）；
2. 全工程搜这个符号的**定义**（注意 `(float)` 这种参数列表，重载时名字一样）；
   - 搜不到 → 你只写了声明，去写定义；
   - 搜得到，在某个 `.cpp` 里 → 那个文件**加进构建系统了吗**（`CMakeLists.txt` 的
     `add_library` / `add_executable`）；工程用的是 CMake，源文件列表是手写的，
     新建 `.cpp` 不会自动参与编译；
3. 定义在头文件里、也包含进来了，那多半是签名对不上（`const` 修饰、参数类型、
   `namespace` 不同），编译器眼里它们是两个不同的符号。

> **工程里在哪见过它**：`base/math.h:8`（inline 定义）、`app/clamp.h:9` + `app/clamp.cpp:3`
> （声明 + 定义）、`app/motor_monitor.cpp:17`（调用点）、`CMakeLists.txt:11-15`（源文件列表）。

---

## 4. `inline`、ODR，以及头文件里的函数

### 4.1 `base/math.h` 里的 `inline` 是干什么的

```cpp
// base/math.h:8-13
inline float deg_normalize_180(float d) {
  if (d > 180.0f) {
    d -= 360.0f;
  }
  return d;
}
```

先问一个问题：把 `inline` 删掉，只留函数定义，会怎样？

- 只有**一个** TU 包含 `base/math.h` 时：编译链接都正常，看起来"`inline` 是多余的"；
- 有**两个以上** TU 包含时：每个 TU 的 `.o` 里都有一份 `deg_normalize_180` 的机器码，
  链接器看到两份**同名强符号**，直接报错：

  ```text
  /usr/bin/ld: b.o: in function `gain(float)':
  b.cpp:(.text+0x0): multiple definition of `gain(float)'; a.o:a.cpp:(.text+0x0): first defined here
  ```

  这个实验的源码和上面这行报错都是实测的（见附录 A）。

`inline` 在这里的作用就是：**告诉链接器"这个函数可能在很多 TU 里都有定义，它们是同一个，
随便挑一份，别报错"。** 这是 `inline` 的主要语义，和"内联展开"是两件事（§4.3）。

这个工程正好是"多个 TU"的情形：`base/math.h` 被 `app/motor_monitor.cpp` 包含，
将来 `app/clamp.cpp`、测试文件都可能有 `clampf` 的需求。所以它必须是 `inline`。

### 4.2 ODR 那句话本身

**ODR = One Definition Rule，单一定义规则。** 用工程里的话说：

- 函数、全局变量：**整个程序里只能有一个定义**。想在多个 TU 里放同一份定义，
  就用 `inline`（或把它放进匿名命名空间 / 加 `static`，那是"每个 TU 一份、互相独立"）。
- 类、`struct`、`enum`、模板：**可以在多个 TU 里各有一份定义**，但要求**逐字相同**
  （token 序列一致）。不一样就是 ODR 违规，症状是各种莫名其妙的链接错误或运行期错乱，
  而且编译器**不保证报错**——这是 C++ 里最难查的一类 bug。
- 每个 `.cpp`（TU）里，同一个名字只允许有一个定义（这条最好理解，缺 include guard
  就是踩这条）。

"逐字相同"这条对头文件的启示：**类型定义只能有一份来源**。这就是 `Mode_e` 必须定义在
`app/arm.h`、而不是在 `control.cpp` 和 `test_clamp.cpp` 里各写一遍的原因。以后你想给
`MotorFeedback` 加个字段，改 `app/arm.h:20-25` 一处，所有 TU 看到的都是同一个布局。

### 4.3 `inline` 的两种含义

| 含义 | 说什么 | 谁关心 |
| --- | --- | --- |
| 链接语义（主要） | 允许多个 TU 各有一份相同定义，链接器合并 | 链接器 |
| 优化提示（附带） | "这个函数短，可以就地展开，省一次调用" | 编译器（它可以不听） |

现代编译器基本自己决定要不要展开，`inline` 关键字对优化的影响很小。
**你写 `inline` 的理由应该是"定义在头文件里"，不是"我觉得调用它太慢"。**

### 4.4 `inline` 不等于 `static`

两种"能在头文件里定义"的办法，语义完全不同：

**`inline`** = 这些多份定义是**同一个实体**，链接器合并成一份。
**`static`** = 每个 TU 一份**独立的副本**，互相看不见。

怎么验证：把 `inline` 去掉、只留函数定义 —— 一个 `.cpp` 包含它时没事，
**两个以上** `.cpp` 包含就报 `multiple definition`。那个报错就是证据，不需要额外工具。
如果写成 `static float deg_normalize_180(...)`，符号会变成小写 `t`（local），
意思是**每个 TU 一份独立副本**，链接器不管。区别在于：函数内 `static` 变量、
函数地址比较、模板实例化，这两种写法行为不一样。**头文件里放工具函数用 `inline`。**

### 4.5 类体里定义的成员函数隐含 `inline`

`app/clamp.h:11`：

```cpp
bool isCalibrating() const { return is_calibrating_; }
```

`app/motor_monitor.h:18`：

```cpp
const MotorData& data() const { return data_; }
```

这两个函数在头文件里、类体内部，**没写 `inline` 也是 `inline`**。所以它们可以被
几十个 TU 包含而不冲突 —— 和函数级 `inline` 是同一个机制：多份定义，链接器合并成一份。

反过来，定义在 `.cpp` 里的成员函数（`Clamp::update`、`Clamp::beginCalibration`）
就是**普通函数**：只能有一份定义，也不能被别的 TU 直接 include 到。

**实践规则**：一行能写完、和成员变量强相关的取数函数（getter），写在类体里；
稍微有点逻辑的（比如 `Clamp::update`）放 `.cpp`。工程里就是这个分界。

### 4.6 `constexpr` 函数与 `inline`

C++17 里 `constexpr` 函数隐含 `inline`，所以头文件里写
`constexpr float f(float x) { ... }` 不需要额外写 `inline`。工程里没有 `constexpr` 函数，
但这条规则在你写"编译期就能算出来的工具函数"时会用到。

### 4.7 什么时候**不**该 `inline`

- 函数体几十行、带循环和分支：展开只会让代码变大。嵌入式上 flash 是硬约束。
- 需要在 `.cpp` 里改实现、不想让所有人都重编译：放 `.cpp`，改完只重编一个文件。
  头文件一改，包含它的所有 TU 全部重编——大工程里这是分钟级的差别。

> **工程里在哪见过它**：`base/math.h:8`、`base/math.h:15`（inline 自由函数）、
> `app/clamp.h:11`、`app/motor_monitor.h:18`（类内定义）、`tests/test_util.h:21`（测试工具）。

---

## 5. `const`、`constexpr` 与常量

### 5.1 `const` 变量

`const` 的意思是"这个对象初始化之后不能再改"。工程里的 `const` 局部变量：

```cpp
// app/control.cpp:33
const ClampState state = g_clamp.update(0.0f, 0.0f);
```

这行的好处不是性能，是**让读代码的人少想一件事**：这个 `state` 后面不会被改。

### 5.2 `const` 成员函数

```cpp
// app/clamp.h:11
bool isCalibrating() const { return is_calibrating_; }
// app/motor_monitor.h:18
const MotorData& data() const { return data_; }
```

成员函数末尾的 `const` 表示"调用它不会修改这个对象"。它有两个实际作用：

1. `const Clamp c;` 这种对象只能调 `const` 成员函数。测试里 `Clamp c;` 是可变的所以没关系，
   但你如果写 `const MotorMonitor& m`，就只能调 `data()` 这类 `const` 函数；
2. 它是**接口承诺**，会传染：`const` 成员函数里改成员变量会立刻编译错误，
   于是"谁改状态"这件事在类型系统里被写清楚了。

`app/control.cpp:33` 那行把返回值存成 `const` 对象，`app/control.cpp:34` 紧接着
`(void)state;`——编译器开了 `-Wunused-variable` 时会警告"定义了没用"，
`(void)` 是显式说"我知道，故意的"。骨架代码里很常见。

### 5.3 `constexpr`：编译期常量

```cpp
// app/control.cpp:7-14
namespace ctrl_params {
constexpr float kDefaultClampSpeed = 4.0f;
constexpr float kJointRate = 0.02f;
constexpr float kChassisRotateRate = 3.0f;
constexpr float kMouseVisionRate = 0.2f;
}  // namespace ctrl_params
```

这段代码有三个值得学的地方：

1. **`constexpr` 要求值在编译期就能算出来。** 于是它一定能放进 ROM/flash，
   不占 RAM，也能当数组长度、模板参数用。`const` 变量理论上也常常被优化掉，
   但 `constexpr` 是**保证**。
2. **集中在一个具名命名空间里。** 注释写着"调参集中在这一块"——这在真实战队工程里是
   一条纪律：参数散落在各文件里，比赛现场调车时会疯。HW5 的 `TODO(hw5-a)` 就是改这里的
   `kDefaultClampSpeed`。
3. `constexpr` 变量隐含 `const` 和 `inline`（C++17），所以放在头文件里被多个 TU 包含
   也不会重复定义。

类里的编译期常量（`app/clamp.h:18`、`:20`）：

```cpp
static constexpr float kResistThreshold = 1400.0f;
static constexpr float kOpenAngle = 900.0f;
```

`static` + `constexpr` 的组合：`static` 表示它属于类而不属于某个对象（没有每个对象一份），
`constexpr` 表示编译期常量。C++17 起这种静态常量**不需要**在 `.cpp` 里再写一遍定义，
直接用就行（`app/clamp.cpp:16` 就直接用了 `kResistThreshold`）。

### 5.4 浮点字面量的 `f`

```cpp
constexpr float kDefaultClampSpeed = 4.0f;    // 对
constexpr float kWrong = 4.0;                 // 也编译得过，但类型是 double
```

`4.0` 是 `double`，赋给 `float` 会发生一次窄化转换。大多数情况编译器会顺手处理掉，
但在嵌入式上，无意中把运算拉到 `double`（软件浮点，慢且占空间）是真实存在的性能坑。
**规则：`float` 类型就写 `4.0f`。** 工程里全都带 `f`（`app/control.cpp:10-13`、
`app/clamp.h:18-20`、`tests/test_encoder.cpp:22-36`）。

### 5.5 `#define` vs `constexpr`

工程里没用宏定义常量，只有 include guard 的宏。原因：

- 宏是预处理期文本替换，**没有类型、没有作用域**，出错时报错信息极难读；
- `constexpr` 有类型、有作用域、能被调试器看到。

嵌入式里唯一还常见 `#define` 的地方是条件编译（`#ifdef STM32F407xx`）和寄存器位定义，
那是另一回事。

> **工程里在哪见过它**：`app/control.cpp:10-13`、`app/clamp.h:18-20`、
> `app/control.cpp:33-34`、`base/math.h:8-9`（`180.0f`）。

---

## 6. 引用与 `const` 引用

### 6.1 引用是别名

```cpp
float a = 1.0f;
float& r = a;      // r 是 a 的另一个名字
r = 2.0f;          // a 也变成 2.0f
```

引用必须在定义时绑定，之后不能改绑到别的对象；引用不能为空。这两条决定了它和指针的分工。

### 6.2 `const MotorData& data() const`

```cpp
// app/motor_monitor.h:18
const MotorData& data() const { return data_; }
```

一行里有三个信息，拆开看：

| 位置 | 含义 |
| --- | --- |
| 返回类型 `const MotorData&` | 返回内部成员的**引用**：不拷贝，调用者拿到的是原对象 |
| 返回类型里的 `const` | 调用者只能读，不能通过这个引用改内部状态 |
| 参数列表后的 `const` | 这个函数不修改对象本身，可以被 `const` 对象调用 |

为什么返回引用而不是值？`MotorData` 有 6 个 `float`（`base/motor.h:6-13`），
按值返回要拷贝 24 字节。更重要的是**语义**：`test_encoder.cpp:16` 的
`return m.data().angle;` 读的是监视器里真实的累计角度，不是一份快照。

为什么加 `const`？如果返回 `MotorData&`，调用者可以写 `m.data().angle = 999.0f`，
绕过所有封装。`const` 引用把"能读不能写"写进了类型。

### 6.3 传参：按值还是按 `const` 引用

工程里的选择非常一致：**小标量按值，大对象按 `const` 引用**。

```cpp
// app/motor_monitor.h:16 —— 三个 float，按值
void update(float raw_angle_deg, float speed_dps, float current_a);
// app/motor_monitor.h:13 —— 一个 float，按值
void reset(float raw_angle_deg);
// app/motor_monitor.h:18 —— 结构体，按 const 引用
const MotorData& data() const;
```

一个 `float` 是 4 字节，引用底层也是地址（8 字节），按值传反而更快、还不用担心里面被改。
经验线大概在 16 字节或者"拷贝有成本"的类型上——超过就按 `const` 引用传。

### 6.4 引用还是指针

| | 引用 | 指针 |
| --- | --- | --- |
| 可以为空 | 不行 | 可以（`nullptr`） |
| 可以改绑 | 不行 | 可以 |
| 语法 | `f(x)` | `f(&x)` / `f(p)` |
| 适合 | 函数参数、返回值（`data()`） | 可选对象、数组遍历、C 接口、硬件寄存器 |

工程里现在一处指针都没有（`test_encoder.cpp:10` 的 `const float* seq` 是数组传参，
是指针唯一合理的用法）。嵌入式里裸指针主要出现在寄存器地址、DMA buffer、
C 语言写的 HAL 接口上。

### 6.5 引用的生命周期陷阱

```cpp
// 错的
const MotorData& bad() {
  MotorData local{};      // 函数结束就销毁
  return local;           // 返回悬垂引用，之后读到的是垃圾
}
```

返回引用时，被引用的对象必须**活得比引用长**。`data()` 安全是因为 `data_` 是对象成员，
对象的生命周期由调用者掌握。编译器对明显的这种错误会警告（`-Wreturn-local-addr`），
但复杂情况下不一定。

### 6.6 一个"返回引用"的真实用法

`tests/test_util.h:11-14`：

```cpp
inline int& checks() {
  static int n = 0;
  return n;
}
```

返回引用是为了让调用者能写 `++checks();`（`tests/test_util.h:22`）直接改那个计数器。
如果返回 `int`，`++checks()` 只会改一个临时副本，测试计数永远是 0——一个经典的、
看起来完全正常但结果不对的 bug。

> **工程里在哪见过它**：`app/motor_monitor.h:18`、`tests/test_util.h:11-19`、
> `app/clamp.cpp:12`（参数按值）、`tests/test_encoder.cpp:16`（读返回值）。

---

### 6.7 真实仓库里长什么样

```cpp
// wheel-legged/base/common/math.cpp:67（原样抄）
float math::loopLimit(float val, const float& min, const float& max) {
  if (min >= max)
    return val;
  if (val > max) {
    while (val > max)
      val -= (max - min);
  } else if (val < min) {
    while (val < min)
      val += (max - min);
  }
  return val;
}

// 同文件 :139
float math::degNormalize180(const float& angle) {
  return math::loopLimit(angle, -180.f, 180.f);
}
```

对着 §6.3 的判断顺序读一遍：

| 参数 | 写法 | 为什么 |
| --- | --- | --- |
| `val` | 按值 `float` | 小、只读、而且函数内部要改它（`val -= ...`）——所以**必须**按值 |
| `min` / `max` | `const float&` | 只读，按队里习惯写成引用 |
| `angle` | `const float&` | 只读 |

`val` 那个按值传**不是风格问题，是功能需要**：函数体里要修改它。
如果写成 `float& val`，这个函数就会把调用方的变量改掉。

顺带看一段和 HW2 直接相关的：`degNormalize180` 就是**编码器回绕**那个概念。
HW2 里 `deg_normalize_180` 的 bug 是只有一个 `if (d > 180)` 分支——
真实仓库这个版本用 `while` 同时处理了两边，而且用 `while` 而不是 `if`，
所以转了好几圈（比如 730°）也能正确折回来。练习工程
`day0/cpp/base/common/math.cpp` 的 TODO(cpp1) 就是让你把它写出来。

---

## 6b. 指针

§6 说"引用不能为空"，那指针就是**可以为空、可以改指**的那种东西。
战队代码里指针的密度比你想象的高：

指针在战队自己的代码里到处都是：`Motor* arr[11]`、`if (p != nullptr)`、`p->update(...)`。
（出现次数的统计口径见 `SYLLABUS.md` §0.1。）

### 6b.1 声明怎么读

指针声明要**从变量名往外读**：

```cpp
Motor* p;                  // p 是一个指针，指向 Motor
Motor** pp;                // pp 是一个指针，指向「指向 Motor 的指针」
Motor* arr[11];            // arr 是一个数组，元素是「指向 Motor 的指针」
float (*f)(float);         // f 是一个指针，指向「接收 float、返回 float 的函数」
float* g(float);           // g 是一个函数，接收 float，返回「指向 float 的指针」
```

最后两条最容易看混。区别在于**括号把 `*` 和谁绑在一起**：
`(*f)` 说明 `f` 先是指针；`*g(...)` 说明 `g` 先是函数。

### 6b.2 真实仓库里长什么样

`wheel-legged/base/motor/driver/dji_motor_driver.h` 里一个类同时用到三种：

```cpp
// wheel-legged/base/motor/driver/dji_motor_driver.h:48（构造函数）
DJIMotorDriver(Motor* can1_motor[11], Motor* can2_motor[11]) {
  memcpy(can1_motor_, can1_motor, 11 * sizeof(Motor*));
  memcpy(can2_motor_, can2_motor, 11 * sizeof(Motor*));
}

// 同文件 :77（成员）
Motor* can1_motor_[11];
Motor* can2_motor_[11];
```

```cpp
// wheel-legged/base/motor/driver/dji_motor_driver.cpp:22（用法）
for (int i = 0; i < 11; i++) {
  if (can1_motor_[i] != nullptr) {
    can1_motor_[i]->CANIdConfig(1, i + 1);
  }
  ...
}
```

三件事一起看：

1. **`Motor* can1_motor[11]` 是"指针数组"** —— 11 个格子，每格存一个地址。
   战队代码里几乎不用 `std::vector<Motor>`，因为固件里不动态分配（§12.4）。
2. **`memcpy(..., 11 * sizeof(Motor*))`** —— 拷的是**地址**，不是电机对象。
   `sizeof(Motor*)` 在 32 位 ARM 上是 4。写成 `sizeof(Motor)` 就错了，而且不会报错。
3. **`!= nullptr` 再 `->`** —— 这两件事必须成对出现。数组里允许有空位
   （某个 ID 上没接电机），所以每个元素都要单独判。

> **`memcpy` 的第三个参数**：真实代码写的是 `11 * sizeof(Motor*)`。
> 更稳的写法是 `sizeof(can1_motor_)`（让编译器自己算），
> 但两种写法在数组不退化时等价。要小心的是**数组作为函数参数时会退化成指针**，
> 那时候 `sizeof` 拿到的是指针大小，不是数组大小 —— 见 §7b.4。

### 6b.3 指针参数与解引用：`isNanOrInf`

```cpp
// wheel-legged/base/common/math.cpp:157
bool math::isNanOrInf(const float* ptr) {
  uint32_t val = *((uint32_t*)ptr);
  uint32_t exponent = (val >> 23) & 0xFF;
  return exponent == 0xFF;
}
```

四行代码，四件事：

| 代码 | 讲的是什么 |
| --- | --- |
| `const float* ptr` | 参数是指针。后面加 `const` 表示**不能通过这个指针改内容** |
| `\*ptr` | 解引用：把地址上的东西取出来 |
| `(uint32_t*)ptr` | **C 风格强转**：把"指向 float 的指针"变成"指向 uint32_t 的指针" |
| `val >> 23` | 位运算：取 IEEE754 的指数位（§6c） |

调用方要传地址：

```cpp
float v = ...;
if (math::isNanOrInf(&v)) { ... }    // & 取地址
```

**为什么要绕这一圈**：正常写法是 `std::isnan(v)`，但 Release 编译用了 `-Ofast`，
它包含 `-ffinite-math-only` —— 编译器会**假定不存在 NaN**，于是 `std::isnan` 被优化成
常量 `false`。所以只能自己看位。（§5.4 讲浮点字面量时提过 `-Ofast`。）

> **这里有个不严谨的地方，你要知道**：`*((uint32_t*)ptr)` 通过一个 `uint32_t*`
> 读一个 `float` 对象，在 C++ 标准里是**未定义行为**（违反严格别名规则）。
> 工程上大家都在这么写，因为 GCC 通常按你期望的方式处理；
> 但更正确的写法是 `memcpy` 或 C++20 的 `std::bit_cast`。
> 读到这种代码时，**照抄可以，但要认得出来它不严谨**。

### 6b.4 指针还是引用

§6.4 说过一轮，这里补上判断标准：

| 场景 | 用哪个 | 为什么 |
| --- | --- | --- |
| 参数"一定存在、不会被改" | `const T&` | 表达"必然有"，调用方不用判空 |
| 参数"可能没有" | `T*`（默认 `nullptr`） | 空是有意义的状态 |
| 要改调用方的变量 | `T&` | 比 `T*` 更明确 |
| 存进成员、以后才用 | `T*` | 引用成员会让类不可赋值 |
| 数组 | `T*` + 长度 | 或者 `T (&arr)[N]` 保留数组类型 |

**战队代码的现实**：`Motor* wheels_` + `int wheel_count_` 这种组合到处都是
（`lab/EC-Training-Labs/day0/cpp/app/chassis.h` 也是照这个抽象来的）——
因为对象数组是在别处建好的，这里只存一个首地址。

### 6b.5 三条最常见的错

```cpp
// ① 野指针：声明了没初始化
Motor* p;
p->update(raw);            // 里面是什么地址？不知道

// ② 解引用空指针
Motor* p = nullptr;
p->update(raw);            // 段错误。前面那句 if (p != nullptr) 不是可选的

// ③ 返回局部变量的地址
Motor* make() {
  Motor m(...);
  return &m;               // m 在函数返回时就没了，这个地址指向垃圾
}
```

第 ③ 条编译器一般会给警告（`-Wall -Wextra` 下），别忽略它。

---

## 6c. 位运算、类型转换与定长类型

这一节讲怎么把几个字节拆开、怎么把两字节拼成一个数。查 CAN 报文要用到，
后面 Day 3 的 CAN 课讲协议本身（字节序、字段含义、ID 规则），两边不重复。

### 6c.1 六个运算符

```cpp
a << n      // 左移 n 位：低位补 0
a >> n      // 右移 n 位：无符号补 0；有符号负数补什么由实现决定（别依赖它）
a & b       // 按位与：常用来"取某些位"（掩码）
a | b       // 按位或：常用来"拼起来"
a ^ b       // 按位异或：翻转
~a          // 按位取反
```

在战队代码里的出现次数（§SYLLABUS §0.1 口径）：
三个最常用的套路：

```cpp
// 取低 8 位
uint8_t  lo = static_cast<uint8_t>(value & 0xFF);
// 取高 8 位
uint8_t  hi = static_cast<uint8_t>((value >> 8) & 0xFF);
// 拼回去（大端：高字节在前）
uint16_t v  = static_cast<uint16_t>((static_cast<uint16_t>(hi) << 8) | lo);
```

> **为什么中间要写 `static_cast<uint16_t>`**：`hi` 是 `uint8_t`，参与运算时会先
> **整型提升**成 `int`（§6c.4）。`hi << 8` 的类型是 `int`，
> 拼完再赋给 `uint16_t` 会触发窄化警告。显式转一次，意图清楚，也不报警告。

### 6c.2 真实仓库里长什么样

```cpp
// wheel-legged/base/motor/driver/dji_motor_driver.cpp:63（原样抄，只看 GM6020 那一路）
      if (motor->info_.type == Motor::GM6020_CURRENT) {
        can_tx_data1_[2 * i] = 0;
        can_tx_data1_[2 * i + 1] = 0;
        can_tx_data2_[2 * i] = (motor->intensity_ >> 8);
        can_tx_data2_[2 * i + 1] = (motor->intensity_);
        is_data2_used = true;
      } else {
        can_tx_data1_[2 * i] = (motor->intensity_ >> 8);
        can_tx_data1_[2 * i + 1] = (motor->intensity_);
        can_tx_data2_[2 * i] = 0;
        can_tx_data2_[2 * i + 1] = 0;
        is_data1_used = true;
      }
```

数组的类型是 `uint8_t can_tx_data1_[8]`（同文件 :79）。所以：

- 第一行：`intensity_`（16 位）右移 8 位 → 高字节 → 赋给 `uint8_t` 时**自动截断**，
  只剩低 8 位。
- 第二行：**没有 `& 0xFF`**。因为赋给 `uint8_t` 这个动作本身就完成了截断。

那为什么还要写 `& 0xFF`？**因为不是所有场合都有这次赋值**。比如：

```cpp
int hi = (value >> 8);        // 没截断！hi 里是完整的 value>>8，高位都是 0 还好
int hi = (value >> 8) & 0xFF; // 明确"我只要这 8 位"
```

**真实代码这段还有一个坑**：`intensity_` 如果是负数，`>> 8` 是**算术右移还是逻辑右移**
由实现决定。要写跨平台的代码，应该先转成无符号：

```cpp
const uint16_t raw = static_cast<uint16_t>(intensity);   // 负数的补码表示
out[2 * i]     = static_cast<uint8_t>(raw >> 8);
out[2 * i + 1] = static_cast<uint8_t>(raw & 0xFF);
```

`day0/cpp/base/motor/dji_motor_driver.cpp` 里的 TODO(cpp4) 就是让你写这一版。

### 6c.3 类型转换：三种写法，三种态度

```cpp
double d = 3.9;
int a = (int)d;                    // ① C 风格强转：什么都转得动，编译器不问
int b = static_cast<int>(d);       // ② 明确：我知道我在截断
uint32_t* p = reinterpret_cast<uint32_t*>(&f);  // ③ 重新解释同一块内存

// ④ 隐式转换：最危险，因为它没有形状
int c = d;                         // 编译过了，3.9 变成 3
```

| 写法 | 战队代码里 | 什么时候用 |
| --- | --- | --- |
| `static_cast<T>(x)` | **242 次** | 默认选它。数值转换、`void*`→具体指针、显式调用构造函数 |
| C 风格 `(T)x` | **114 次** | 老代码里到处都是。**新代码别写** —— 它可能是上面任意一种，看的人要猜 |
| `reinterpret_cast<T*>(p)` | 16 次 | 只在"同一块内存按另一种类型读"时用，比如 §6b.3 那个 `isNanOrInf` |
| `const_cast` | 0 次 | 去掉 `const`。战队代码里没人用，你也不该用 |
| 隐式转换 | 到处都是 | 缩小范围时危险（`float` → `int16_t`） |

**为什么新代码不该写 C 风格强转**：`(int)d` 和 `(uint32_t*)ptr` 长得几乎一样，
但一个是数值转换、一个是重新解释内存，风险完全不同。`static_cast` /
`reinterpret_cast` 把这件事写在脸上。

> **实战判断法**：看到一个 C 风格强转，先问"它其实是哪一种"。
> 如果是数值转换，说明作者懒得写 `static_cast`；如果是重新解释内存，
> 说明这里可能有严格别名问题（§6b.3）。

### 6c.4 整型提升与有符号 / 无符号

这是最容易写出"能编译、结果错"的地方。

```cpp
uint8_t a = 200, b = 100;
auto c = a + b;          // c 是 int，值 300 —— 不是 uint8_t，也不溢出
uint8_t d = a + b;       // d 是 44（300 截断到 8 位）

if (a - b < 0) { ... }   // a - b 是 int，-100? 不，是 100。见下
```

规则（C++ 的"整型提升"）：

1. 比 `int` 窄的类型（`char` / `uint8_t` / `int16_t`）参与运算前，
   **先提升成 `int`**。
2. 所以 `uint8_t - uint8_t` 的结果类型是 `int`，**不会是负数**（只要两个数都在 0~255）。
3. 混用有符号和无符号时，有符号会被转成无符号 —— 负数变成巨大的正数，
   这是经典 bug。

真实代码里有一条，和这个直接相关：

```cpp
// wheel-legged/base/common/math.cpp:157 附近
bool math::isNanOrInf(const float* ptr) { ... }
```

它是先 `(uint32_t*)ptr` 再取位 —— 全程无符号，规避了右移的符号问题。

**实用建议**：要按位操作、要做掩码，就一路用无符号（`uint8_t` / `uint16_t` /
`uint32_t`）；要算术，就一路用有符号。别在一行里混。

### 6c.5 定长类型：`<cstdint>`

```cpp
#include <cstdint>

int8_t  a;   uint8_t  b;    // 恰好 8 位
int16_t c;   uint16_t d;    // 恰好 16 位
int32_t e;   uint32_t f;    // 恰好 32 位
```

**`int` 的宽度不作保证**（标准只说"至少 16 位"）。在 STM32 上它是 32 位，
但这不是你依赖它的理由。凡是**和外部世界交换数据**的地方，都必须用定长类型：

- CAN / 串口报文的每个字段
- 寄存器读写
- 协议结构体

真实代码里全是定长类型：

```cpp
// wheel-legged/base/motor/driver/dji_motor_driver.h:77（CAN 报文缓冲）
uint8_t can_tx_data1_[8];  // 0x200, 0x1FF, 0x2FF
uint8_t can_tx_data2_[8];  // 0x1FE, 0x2FE

// 同文件 :44（电调反馈）
typedef struct RawData {
  int16_t ecd;               // encoder value(0~8191) 编码器值(0~8191)
  int16_t rotate_speed_rpm;  // rotational speed(rpm) 转速(单位rpm)
  int16_t torq_current;      // torque current 转矩电流
  int8_t temp;               // temperature 温度
} RawData_t;
```

> **`int8_t temp`**：温度用一个**有符号** 8 位。为什么不是 `uint8_t`？
> 因为协议规定的。这就是定长类型的意义 —— 它对齐的是**协议**，不是你的方便。

### 6c.6 结构体布局：为什么不能拿 struct 直接盖上去

```cpp
// 想这么干？不行。
RawData_t d;
memcpy(&d, rx_data, sizeof(RawData_t));   // ← 字段会错位
```

因为编译器会在结构体成员之间插 **padding（填充）**，让每个成员落在对齐的地址上：

```text
真实的内存布局（32 位 ARM，默认对齐）：

  偏移 0   int16_t ecd                 (2 字节)
  偏移 2   int16_t rotate_speed_rpm    (2 字节)
  偏移 4   int16_t torq_current        (2 字节)
  偏移 6   int8_t  temp                (1 字节)
  偏移 7   [padding]                   (1 字节) ← 为了整个结构体对齐到偶数
  sizeof = 8
```

这个例子里刚好凑巧是 8 字节、字段也没错位 —— **但这是运气**。换一个字段顺序：

```cpp
struct Bad {
  int8_t  a;    // 偏移 0
  int32_t b;    // 偏移 4（前面插了 3 字节 padding！）
  int8_t  c;    // 偏移 8
};              // sizeof = 12，不是 6
```

所以正确做法是**逐字段用位运算拼**，就像 §6c.1 那样。

> **`#pragma pack(1)` 能不能用**：能，它让编译器不插 padding。
> 但你会得到一个"非对齐访问"的结构体，在有些架构上直接硬件异常；
> 而且这个 pragma 是**非标准扩展**，换个编译器行为可能不同。
> 战队代码里没有用它 —— 遇到协议就用位运算手拼。

---

## 7. 类与成员初始化

### 7.1 `class` 和 `struct` 的区别

只有一条：默认访问权限。`class` 默认 `private`，`struct` 默认 `public`。
工程里的用法很典型：

- `app/arm.h:20` 的 `struct MotorFeedback`、`base/motor.h:6` 的 `struct MotorData`：
  **纯数据**，成员全公开，没有行为；
- `app/clamp.h:7` 的 `class Clamp`：**有行为、有内部状态**，所以成员变量是 `private`，
  只暴露函数。

这不是语法规定，是约定。看到 `class` 就知道"里面有不希望你碰的东西"。

### 7.2 默认成员初始化器（NSDMI）

```cpp
// base/motor.h:6-13
struct MotorData {
  float angle = 0.0f;           // 累计角度
  float ecd_angle = 0.0f;       // 本次编码器角度
  float last_raw_angle = 0.0f;  // 上次编码器角度
  float speed = 0.0f;           // 转速
  float current = 0.0f;         // 转矩电流
  float temp = 0.0f;            // 温度
};
```

`app/arm.h:20-25`、`app/clamp.h:22-23` 也是同样的写法。

这是 C++11 的**默认成员初始化器**（default member initializer）。它的价值在嵌入式里很大：
**没有它，"忘了初始化"就是随机值**——C 里 `struct MotorData d;` 的成员是不确定的，
真机上表现为"偶尔第一帧数据是天文数字"。有了 `= 0.0f`，
`MotorData d;` 就会把每个成员初始化成 0。

注意：规范写法是 `= 0.0f` 或者 `{0.0f}` 都行，但**别写 `MotorData d = {0}`**这种混合风格，
工程里统一用 NSDMI。

### 7.3 这个工程里没有手写构造函数

`MotorData`、`MotorFeedback`、`Clamp`、`MotorMonitor` 都没有构造函数。原因是：

- 成员都有 NSDMI，默认构造出来的对象已经是确定的初值；
- `Clamp` / `MotorMonitor` 的"初始化"动作被显式做成了函数
  （`beginCalibration()`、`reset()`），因为这些动作**可能失败、可能需要在运行中重做**，
  而构造函数只能跑一次、还没法返回错误。

这是嵌入式 C++ 里很常见的一种风格：**对象构造得尽量简单（全 0 / 全 false），
真正的初始化写成显式函数，由调度层在合适的时机调用**。
`app/control.cpp:24-29` 的 `controlInit()` 就是这个"合适的时机"：

```cpp
void controlInit() {
  g_joint_monitor.reset(0.0f);
  g_clamp.beginCalibration();
  g_clamp.endCalibration();
  g_mode = Mode_e::FOLD;
}
```

### 7.4 `MotorData{}` 与 `MotorData`

```cpp
// app/motor_monitor.cpp:5-7
void MotorMonitor::reset() {
  data_ = MotorData{};
}
```

`MotorData{}` 是**值初始化**：构造一个临时对象（成员按 NSDMI 归零），然后赋值给 `data_`。
写成 `data_ = MotorData();` 效果一样。如果写成 `MotorData d;` 那叫默认初始化，
**对聚合类型来说成员会按 NSDMI 处理**（这里有 NSDMI 所以也是 0），
但**如果哪天有人给某个成员去掉了 NSDMI，`d;` 就变成不确定值了**。
`{}` 是更稳的写法，工程里统一用它。

成员声明处的那个 `{}`（`app/motor_monitor.h:21`）是另一回事：

```cpp
MotorData data_{};
```

这是"用空列表初始化这个成员"，等价于在这里写了个 NSDMI。作用一样：保证任何构造路径下
`data_` 都被归零。嵌入式代码里看到 `_` + `{}` 的组合，基本就是这个意思。

### 7.5 成员初始化列表

工程里因为没有构造函数，看不到初始化列表。真实工程里它长这样：

```cpp
// 示意（不在 day0/project 里）：成员初始化列表
class Pid {
 public:
  Pid(float kp, float ki, float kd) : kp_(kp), ki_(ki), kd_(kd) {}

 private:
  float kp_;
  float ki_;
  float kd_;
};
```

冒号后面那串就是初始化列表。关键点：**成员真正的初始化发生在初始化列表里，
构造函数体里写的是赋值。** 对 `const` 成员、引用成员、没有默认构造函数的成员类型，
只能走初始化列表。工程里的 `.clang-format:20` 还专门配了
`BreakConstructorInitializers: AfterColon`，说明这套风格来自真实工程。

初始化顺序由**成员声明顺序**决定，不是初始化列表里的顺序。这个坑很隐蔽：
列表里写反了顺序，编译器 `-Wreorder` 会警告。

### 7.6 封装的边界

```cpp
// app/clamp.h:11      公开：问一句"在标定吗"
bool isCalibrating() const { return is_calibrating_; }
// app/clamp.h:22      私有：状态本身
bool is_calibrating_ = false;
```

HW5 的 Task 3 要你改 `Clamp::update`，让它在标定期间跳过阻力判断，用的就是
`is_calibrating_`（或 `isCalibrating()`）。这里能看出封装的实际价值：
`is_calibrating_` 只能在 `Clamp` 的函数里改，所以"标定状态什么时候被置位"这个问题
只有一个答案（`beginCalibration()` / `endCalibration()`），调试时不用满工程搜。

命名约定也是接口的一部分：成员变量带尾下划线（`state_`、`data_`、`is_calibrating_`），
编译期常量带 `k` 前缀（`kResistThreshold`、`kDefaultClampSpeed`）。看到名字就知道是什么。

### 7.7 重载

```cpp
// app/motor_monitor.h:9,13
void reset();
void reset(float raw_angle_deg);
```

同名不同参数叫**重载**（overload）。编译期按实参类型选一个，`app/control.cpp:25`
的 `g_joint_monitor.reset(0.0f)` 会选第二个。

重载 vs 默认参数（`void reset(float raw = 0.0f);`）怎么选？这里分开写是有意的：
`reset()`（不给基准角）和 `reset(float)`（把基准角设成当前角度）语义不同，
分开写能各自写注释（`app/motor_monitor.h:9-13`）。参数少、语义清楚时用默认参数更省事，
语义不同就该重载。

### 7.8 `this`

成员函数里的 `this` 是指向当前对象的指针，`this->state_` 就是 `state_`。工程里没有显式
使用 `this`——因为成员变量都带 `_` 后缀，不会和参数撞名：

```cpp
// app/motor_monitor.cpp:15-18
void MotorMonitor::update(float raw_angle_deg, float speed_dps, float current_a) {
  data_.angle += deg_normalize_180(raw_angle_deg - data_.last_raw_angle);
```

参数 `raw_angle_deg` 和成员 `data_.last_raw_angle` 一眼能分清。**如果命名不区分，
就必须写 `this->x = x;`**，那说明命名该改。

> **工程里在哪见过它**：`base/motor.h:6-13`、`app/arm.h:20-25`、`app/clamp.h:7-24`、
> `app/motor_monitor.h:9-21`、`app/motor_monitor.cpp:5-13`、`app/control.cpp:24-29`。

---

### 7.9 真实仓库里长什么样（一）：构造函数的初始化列表

```cpp
// wheel-legged/base/motor/motor.cpp:36（简化参数列表，结构原样）
Motor::Motor(const Type_e& type, const float& ratio, const ControlMethod_e& method,
             const PID& ppid, const PID& spid, bool use_kf, const KFParam_t& kf_param,
             float (*model)(const Motor&, const float&, const float&))
    : type_(type),
      ratio_(ratio),
      method_(method),
      ppid_(ppid),
      spid_(spid),
      use_kf_(use_kf),
      kf_param_(kf_param),
      model_(model) {
  ...
}
```

§7.5 讲过初始化列表"比在函数体里赋值更快、而且是唯一能初始化 `const` 成员和引用的地方"。
真实代码里就这么写：**参数名去掉尾部下划线就是成员名**（`type` → `type_`），
一眼能对上。

真实那一份的构造函数参数比这里多得多（PID、卡尔曼参数……），
这里只留了讲得清的那部分。

### 7.10 真实仓库里长什么样（二）：纯虚接口

§7.6 说"封装要有边界"。当边界需要**运行时才知道用哪个实现**时，就需要虚函数：

```cpp
// dual-arm/MasterArm/app/arm.h:174（原样抄）
ArmCore();

virtual ~ArmCore() = default;

virtual void init() = 0;
virtual void reInit() = 0;

virtual void handle() = 0;
```

三个细节：

1. **`= 0` 叫"纯虚函数"** —— 只声明、不实现，`ArmCore` 因此是**抽象类**，
   不能直接创建对象。必须有一个子类把这三个都实现了才行。
2. **`virtual ~ArmCore() = default`** —— 析构函数必须是虚的。
   否则通过基类指针 `delete` 子类对象时，子类的析构函数不会被调用（§7.6 提过）。
   `= default` 表示"用编译器生成的版本"。
3. **它定义的是"一块机械臂要会做什么"**，不是"怎么做"。
   `MasterArm` 和 `SlaveArm` 各有各的实现。

> **为什么真实代码里虚函数只有 21 处**：多态有代价 —— 每个对象多一个虚表指针、
> 每次调用多一次间接跳转，而且分支预测不了。固件里能编译期定下来的就编译期定，
> 所以只有"确实要在运行期换实现"的地方才用（比如这个双臂通信、裁判系统 UI）。
> §11b.2 的模板是另一条路：**把选择挪到编译期**。

---

## 7b. 函数

§7 讲的是"类把数据和行为绑在一起"。但在战队代码里，**自由函数**（不属于任何类的函数）
是更大的那一半：`math::limit`、`math::degNormalize180`、`crc16`、`parseRawData`……
数下来有 1052 个函数定义。

这一节讲两件事：函数怎么写、参数怎么传。

### 7b.1 函数放在哪：三种写法

| 写法 | 放哪 | 什么时候用 | 例子 |
| --- | --- | --- | --- |
| 自由函数 | 命名空间里 | 纯计算，不需要状态 | `math::limit` |
| 类成员函数 | 类里 | 需要访问对象状态 | `Motor::setTorque` |
| `static` 成员函数 | 类里 + `static` | 和类相关、但不需要对象 | `Motor::defaultParam()` |

自由函数用**命名空间**分组，不是用类：

```cpp
// 练习工程 base/common/math.h
namespace math {
float limit(float val, float min, float max);
float loopLimit(float val, const float& min, const float& max);
float degNormalize180(float angle);
bool  isNanOrInf(const float* ptr);
}  // namespace math
```

真实仓库也是这个结构（`wheel-legged/base/common/math.h` 里有二十多个函数，
全在 `namespace math` 里）。**为什么不用类**：这些函数之间没有共享状态，
硬塞进一个类只会多一层 `math::` 之外的前缀和一堆 `static`。

### 7b.2 参数怎么传：三种选择

```cpp
void f(Motor m);              // ① 按值：拷贝一份，改它不影响调用方
void g(Motor& m);             // ② 引用：改它会改到调用方那个对象
void h(const Motor& m);       // ③ const 引用：不拷贝，也不能改
```

判断顺序：

1. **要改调用方的对象吗？** 要 → ②
2. **拷贝贵吗？** 贵（结构体、类）→ ③
3. **小到 4~8 字节的内建类型**（`int` / `float` / 指针 / 枚举）→ ①，拷一下比解引用还快
4. 剩下的（只读、但对象大） → ③

真实代码里两种都混着用，**而且同一个文件里就不一致**：

```cpp
// wheel-legged/base/common/math.h
float limit(float val, float min, float max);                    // 全按值
float loopLimit(float val, const float& min, const float& max);  // 后两个按 const 引用
float sign(const float& val);                                    // 按 const 引用
float deadBand(float val, const float& min, const float& max);   // 混合
```

`float` 只有 4 字节，按值传反而更快（引用本质是指针，多一次内存访问）。
所以 `limit` 的写法是更优的，`loopLimit` 的写法是队里的习惯。

> **你该学的是**：看懂两种都行，知道各自的成本；
> **新写的代码**按上面的判断顺序选，别因为"看到别人这么写"就照抄。
> 一致性重要，但知道为什么不一致更重要。

### 7b.3 默认参数

```cpp
// wheel-legged/base/motor/motor.h:68（简化了前几个参数）
Motor(const Type_e& type, const float& ratio, const ControlMethod_e& method,
      const PID& ppid, const PID& spid, bool use_kf,
      const KFParam_t& kf_param = KFParam_t(2, 1e4, 1, 0.75, 50),
      float (*model)(const Motor&, const float&, const float&) = nullptr);
```

值得看的是默认参数里前面那个：

```cpp
const KFParam_t& kf_param = KFParam_t(2, 1e4, 1, 0.75, 50)
```

**不传就用这套默认的卡尔曼参数。** 这是默认参数最典型的用法：
给一个"大多数情况下够用"的值，让调用方只在需要调的时候才写出来。

规则：

```cpp
void f(int a, int b = 1, int c = 2);   // ✅ 有默认值的必须排在右边
void g(int a = 1, int b);              // ❌ 编译错误
```

> 真实代码里不传这个参数的调用到处都是 —— 也就是绝大多数电机
> 用的都是这套默认值。**只有真去调过参的电机才写出来。**
> 这本身就是一种文档：看到有人传了 `kf_param`，就知道这台电机被单独调过。

### 7b.4 数组参数会退化成指针

上面 `memcpy(..., 11 * sizeof(Motor*))` 那句值得单独说：

```cpp
void f(Motor* arr[11]) { sizeof(arr); }   // 4（32 位下是指针大小），不是 44
void f(Motor  arr[11]) { sizeof(arr); }   // 同样是 4
```

**数组作为函数参数时，类型会退化成指针，长度信息丢失。**
所以：

- 想用 `sizeof` 拿长度 → 必须在**数组还在作用域里**的地方算（比如 `sizeof(arr)/sizeof(arr[0])`）
- 传数组给函数 → 要么额外传一个长度参数，要么用引用保留类型：`void f(Motor (&arr)[11])`
- 真实代码的做法是**额外传长度**：`Chassis(motor::Motor* wheels, int wheel_count, ...)`

### 7b.5 lambda：看得懂就行

真实代码里有 64 处 lambda，基本都是一行的比较器或小谓词：

```cpp
std::sort(v.begin(), v.end(), [](int a, int b) { return a > b; });
```

读法：

```text
[捕获列表](参数列表) { 函数体 }
    ↑
  空 = 不捕获外部变量，等价于一个普通函数
  [&] = 按引用捕获外面所有用到的变量
  [=] = 按值捕获
```

**你只需要能读懂，不要求写。**

---

## 8. 枚举与 `enum class`

`app/arm.h` 里有两种枚举，正好是一个对照实验。

### 8.1 C 风格枚举：`enum Mode_e`

```cpp
// app/arm.h:8-17
enum Mode_e : uint8_t {
  FOLD,
  CRUISE,
  TWIST,
  EXCHANGE,
  STORAGE_FRONT,
  STORAGE_BACK,
  // TODO(hw5-c): ... 加一个独立的工作模式 CALIBRATE。
};
```

两个特点：

- **枚举名会泄漏到外层作用域**。`FOLD` 现在是一个全局名字。工程里 `FOLD`、`TWIST`
  这种名字还算安全，但如果叫 `IDLE`、`ERROR`，大概率会和别处的宏或变量撞名；
- **会隐式转成整数**，也能从整数隐式转回来（要 `static_cast`，但很容易写）。
  所以 `if (mode == 3)` 是能编译的，改枚举顺序就会静默出错。

`: uint8_t` 是**指定底层类型**（C++11）。指定之后：大小确定（1 字节）、
可以前置声明、放进通信结构体时布局可控。嵌入式里几乎总是要指定。
`uint8_t` 来自 `<cstdint>`，所以 `app/arm.h:4` 包含了它。

用的时候两种写法都行（C++11 起，无限定作用域的枚举也支持限定名）：

```cpp
Mode_e g_mode = Mode_e::FOLD;        // app/control.cpp:20，推荐这种
if (mode == FOLD) { ... }            // 也能编译，但不推荐
```

### 8.2 `enum class`：`ClampState`

```cpp
// app/arm.h:28-33
enum class ClampState : uint8_t {
  kIdle,
  kMoving,
  kBlocked,
  kHolding,
};
```

**`enum class`（限定作用域的枚举）修掉了上面两个问题**：

- `kIdle` 不再泄漏，必须写 `ClampState::kIdle`（`app/clamp.cpp:17`、`:22`、
  `tests/test_clamp.cpp:11-18` 全都是这么写的）；
- 不会隐式转成 `int`，也就不可能 `if (state == 2)` 这种写法混进来。

代价是每次都要写全名。工程里用 `k` 前缀（`kBlocked`）让长名字读起来轻一点。
**新代码默认写 `enum class`；只有当这个枚举要和协议字段、寄存器值做整数映射时，
才考虑 C 风格枚举。**

### 8.3 `switch` 覆盖枚举

```cpp
// tests/test_clamp.cpp:9-21
const char* name(ClampState s) {
  switch (s) {
    case ClampState::kIdle:    return "kIdle";
    case ClampState::kMoving:  return "kMoving";
    case ClampState::kBlocked: return "kBlocked";
    case ClampState::kHolding: return "kHolding";
  }
  return "?";
}
```

注意三点：

1. **没有 `default`**，这是刻意的。`-Wall` 下如果漏了一个枚举值，编译器会直接告诉你：

   ```text
   warning: enumeration value 'kHolding' not handled in switch [-Wswitch]
   ```

   写了 `default` 反而会把这条提醒吞掉。这是"让编译器帮你找漏分支"的标准做法。
2. 函数末尾的 `return "?";` 不是死代码——编译器不保证 `switch` 覆盖了所有取值
   （枚举变量可能是非法值），所以必须有个兜底返回，否则 `-Wreturn-type` 会警告。
3. **这个工程默认没开 `-Wall`**（`CXX_FLAGS = -g -std=gnu++17`）。自己写代码时建议
   在本地开一次 `-Wall -Wextra` 看一遍警告。

### 8.4 枚举是"追加点"

`app/arm.h:7` 的注释值得抄在本子上：

> 注意：这个枚举是"追加点"——新功能往里加一个值就行了，所以谁都来加。

这就是 HW5 里冲突的来源：你为了标定加了 `CALIBRATE`，队友为了另一件事加了 `DROP_MODE`，
两个人改的是同一个文件的同一小块区域，Git 只能报冲突。**知道"这个文件谁都会动"，
就应该在改它之前先同步一次，改完尽快推。**

> **工程里在哪见过它**：`app/arm.h:8-17`、`app/arm.h:28-33`、`app/clamp.cpp:16-25`、
> `tests/test_clamp.cpp:9-21`、`app/control.cpp:20`、`:28`。

---

### 8.5 真实仓库里长什么样

§8.1 说"C 风格枚举在战队代码里是主流"。真实的样子：

```cpp
// wheel-legged/base/motor/driver/dji_motor_driver.h:24（原样抄）
namespace djimotor {

typedef enum CANIDRange {
  ID_1_4,
  ID_5_8,
  ID_9_11,
} CANIDRange_e;

typedef enum CANRxError {
  NO_ERROR,
  ID_OUTRANGE,
  MOTOR_UNDEFINED,
  TYPE_MISMATCH,
} CANRxError_e;

// 同文件 :41
typedef struct RawData {
  int16_t ecd;               // encoder value(0~8191) 编码器值(0~8191)
  int16_t rotate_speed_rpm;  // rotational speed(rpm) 转速(单位rpm)
  int16_t torq_current;      // torque current 转矩电流
  int8_t temp;               // temperature 温度
} RawData_t;

};  // namespace djimotor
```

**`typedef enum {...} Name_e;` 是 C 的写法**，C++ 里其实不需要 `typedef`
（直接 `enum Name_e {...};` 就行，C++ 会把 `Name_e` 当类型名）。
真实仓库大量这么写，是因为这些头文件要给 C 代码 include —— 
C 里不写 `typedef`，`Name_e` 就只是个枚举**标签**，不能当类型用。

| 写法 | 谁需要 | 你会看到 |
| --- | --- | --- |
| `typedef enum {...} X_e;` | C 和 C++ | 战队老代码、HAL 代码 |
| `enum X_e {...};` | 只要 C++ | 少数新代码 |
| `enum class X : uint8_t {...}` | 只要 C++ | 练习工程、少数新代码 |

三种都要认得。**写新代码时用 `enum class`**（§8.2 讲了原因：不会隐式转成整数）。

注意 `RawData_t` 的成员类型：`int16_t` / `int8_t` —— **定长类型**，
因为它要和 CAN 协议对齐。为什么这很重要，见 §6c.5。

---

## 9. 命名空间

### 9.1 命名空间解决什么

两个模块都有 `init()`、都有 `kMaxSpeed` 时，命名空间让它们共存。
工程里的 `namespace testutil`（`tests/test_util.h:9`）和 `namespace ctrl_params`
（`app/control.cpp:7`）就是同一件事的两个用法：一个是"测试工具"，
一个是"控制参数"。

### 9.2 具名命名空间

```cpp
// app/control.cpp:7-14
namespace ctrl_params {
constexpr float kDefaultClampSpeed = 4.0f;
constexpr float kJointRate = 0.02f;
// ...
}  // namespace ctrl_params
```

使用时要写 `ctrl_params::kDefaultClampSpeed`（`app/control.cpp:35`）。
结尾那行 `// namespace ctrl_params` 注释是约定：长文件里能一眼看出这个命名空间在哪结束
（`tests/test_util.h:47`、`app/control.cpp:14`、`:22` 都写了）。

### 9.3 匿名命名空间 = 内部链接

```cpp
// app/control.cpp:16-22
namespace {

MotorMonitor g_joint_monitor;
Clamp g_clamp;
Mode_e g_mode = Mode_e::FOLD;

}  // namespace
```

匿名命名空间的成员**只在当前 TU 可见**，外部链接不到。这就是"模块私有全局变量"的
标准写法。用 `nm` 看 `control.cpp.o` 的符号表，一眼就能分辨：

怎么确认它们真的"只在本文件可见"：**在另一个 `.cpp` 里写 `extern` 引用它们，链接会报
`undefined reference`** —— 因为那份符号压根没导出。反过来，把 `namespace { }` 去掉，
同样的代码就能链上了。

（附录 A.2 有这三份目标文件的完整符号表实测输出，想看得更细可以翻。）
**大小写就是"是否对外可见"的标记**——这是读链接错误时最有用的一个工具，
完整对照表见 §11.3。

为什么不直接把这三个对象写在 `.cpp` 文件作用域？可以，效果一样。匿名命名空间的好处是
把"这是内部状态"写得更明确，也顺便避开了和宏重名的可能。

### 9.4 `static` 与匿名命名空间

```cpp
static MotorMonitor g_joint_monitor;    // 老写法，内部链接，效果相同
```

C 时代的写法。C++ 里推荐匿名命名空间，因为它对类型、函数、变量一视同仁
（`static` 不能修饰类型）。工程里两种都没混用，统一用了匿名命名空间。

### 9.5 `using namespace` 的坑

```cpp
using namespace std;      // 别写在头文件里
```

写在头文件里，所有包含它的 TU 都会被迫接受 `std` 里成百上千个名字，
`count`、`size`、`distance` 这类常见名字随时可能和你的变量/函数撞上，
而且报错信息会变得没法读。**头文件里一律写全名（`std::`）；**
`.cpp` 里也建议别写，工程里一处都没省（`tests/test_util.h:23` 的
`std::fabs`、`:25` 的 `std::printf`、`:34` 的 `std::strcmp`）。

命名空间别名（`namespace fs = std::filesystem;`）是另一回事，那个可以放心用。

> **工程里在哪见过它**：`app/control.cpp:7-22`、`tests/test_util.h:9-47`、
> `tests/test_encoder.cpp:7-19`（测试里的匿名命名空间工具函数）。

---

## 10. `static` 的三种含义

同一个关键字，在三个位置是三个意思。这是 C++ 里最容易被误读的关键字。

### 10.1 文件作用域的 `static` → 内部链接

```cpp
static float s_gain = 1.0f;    // 只有这个 .cpp 看得见
```

和匿名命名空间等价（§9.4）。工程里没用这种写法，但你在老代码里一定会见到。

### 10.2 函数内的 `static` → 静态存储期

```cpp
// tests/test_util.h:11-14
inline int& checks() {
  static int n = 0;
  return n;
}
```

`n` 在**第一次执行到这行时初始化一次**，之后一直活着，直到程序结束。
它不在栈上，所以函数返回后它的值还在——这就是测试计数器能累加的原因
（`tests/test_util.h:22` 的 `++checks()`）。

两个必须知道的细节：

1. **C++11 起，初始化是线程安全的**（编译器会加保护），有微小开销；
2. **在 `inline` 函数里的 `static` 变量，全程序共用一份**，不是每个 TU 一份。
   证据是符号表里的 `u`：

   `checks()` 定义在头文件里、被多个 TU 包含，所以严格说每个 TU 都会有一份 `n`；
   链接器把它们合并成一个 —— 这是"头文件里的 `inline` 函数里的 `static` 变量"
   该有的行为。（附录 A.4 有符号表实测，想确认可以翻。）

**嵌入式上的注意点**：函数内 `static` 意味着这个函数**不可重入**。
如果它会被中断和主循环同时调用，就会出现竞态。工程里 `checks()` 只在 main 里用，
没有这个问题；但你以后在 CAN 回调、中断里写 `static` 计数器时要停下来想一秒。

### 10.3 类里的 `static` → 属于类，不属于对象

```cpp
// app/clamp.h:18
static constexpr float kResistThreshold = 1400.0f;
```

`kResistThreshold` 不在每个 `Clamp` 对象里，`sizeof(Clamp)` 也不包含它。
所有对象共用一份（而且这里因为 `constexpr`，直接编进指令里了，连存储都不占）。

### 10.4 三者对照

| 写法 | 链接性 | 生命周期 | 谁共享 |
| --- | --- | --- | --- |
| 文件作用域 `static` | 内部 | 程序 | 本 TU |
| 匿名命名空间 | 内部 | 程序 | 本 TU |
| 函数内 `static` | 跟随函数 | 程序（首次调用时初始化） | 全程序（inline 函数里也是） |
| 类内 `static` 成员 | 跟随类 | 程序 | 全程序 |

> **工程里在哪见过它**：`tests/test_util.h:11-19`、`app/clamp.h:18`、`:20`、
> `app/control.cpp:16-22`。

---

## 11. 编译单元与链接

### 11.1 从源码到可执行文件

```text
app/control.cpp ─┐
app/motor_monitor.cpp ─┼─→ 编译（每个文件独立） ─→ .o ─→ ar ─→ libday0_core.a
app/clamp.cpp ─┘                                              │
                                                              ↓
tests/test_encoder.cpp ─→ 编译 ─→ test_encoder.cpp.o ─→ 链接 ─→ test_encoder（可执行）
                                                              ↑
                                                        C++ 标准库 / 启动代码
```

`libday0_core.a` 是**静态库**：一堆 `.o` 的归档包。链接时，
链接器只从里面挑"被用到"的目标文件。它的好处是"改一个 `.cpp` 只重编那一个"，
以及"库可以被多个可执行文件复用"（本工程里 `test_encoder` 和 `test_clamp` 都用它，
见 `tests/CMakeLists.txt:2`、`:6`）。

### 11.2 静态库不检查符号

HW3 里那个未定义符号，`libday0_core.a` **照样生成成功**。原因：`.a` 只是打包，
不解析引用。链接一个**可执行文件**时才会做符号解析，那时才发现缺东西。

真实输出里这一行说明了一切：

```text
[ 50%] Linking CXX static library libday0_core.a     ← 库成功
[ 75%] Linking CXX executable test_encoder           ← 这里才炸
```

记住这个顺序，你以后看到"库编过了但程序链不过"就不会困惑。

### 11.3 链接错误怎么读（不需要额外工具）

链接报错就那么几种，看**报错原文**就够了：

```text
/usr/bin/ld: tests/test_encoder.cpp.o: in function `main':
tests/test_encoder.cpp:8: undefined reference to `math::limit(float, float, float)'
collect2: error: ld returned 1 exit status
```

**`undefined reference to X`** —— 链接器在找 `X` 的定义，没找到。三件事依次查：

| 查什么 | 怎么查 |
| --- | --- |
| ① 这个函数**写了吗**？ | 在工程里搜函数名（IDE 里 `Ctrl+Shift+F`），看是只有声明还是也有函数体 |
| ② 写了的话，**加进构建系统了吗**？ | 看 `CMakeLists.txt` 的 `add_library` 列表里有没有那个 `.cpp`（§11.4） |
| ③ 名字**对得上吗**？ | 声明和定义的参数、`const` 有没有写岔；是不是忘了 `extern "C"`（§14） |

**报错里指的文件是"调用点"，不是"缺失的地方"** —— 这一点最容易看错。
上面那条报的是 `test_encoder.cpp:8`，但问题不在那儿，在 `math::limit` 没有定义。

**`multiple definition of X`** —— 反过来：同一个名字有好几份定义。
最常见的原因是**头文件里写了普通函数，被多个 `.cpp` include**（§4.2）。

> **想加深再看**：如果本机有 `nm`（装了 MinGW-w64 或者 Linux 就有），
> 可以用它看目标文件里的符号：`nm -C app/control.cpp.o`。
> 第一列的字母 `T`（有定义）、`U`（只用到、没定义）、`W`（弱符号，`inline` 就是这种）
> 能让你在报错之前就发现问题。
>
> **但这不是必须的。** 上面那三种报错足够定位绝大多数链接问题，
> 而且它们不需要装任何东西。战队日常排查也主要靠报错原文 + 搜代码。
>
> 完整的三份符号表实测输出收在附录 A.2，好奇的时候再翻。

### 11.4 "文件写了但没加进构建系统"

`CMakeLists.txt` 里的源文件列表是**手写的**：

```cmake
add_library(day0_core
  app/control.cpp
  app/motor_monitor.cpp
  app/clamp.cpp
)
```

新建 `base/angle.cpp` 而不加这一行，它根本不会被编译。症状与"函数没写"完全一样：
`undefined reference`。这是 HW3 做法 A 的主要坑。

真实工程里这件事的变体更多：CMake 的 `target_sources`、Keil 的 `.uvprojx` 文件列表、
Makefile 的 `SRCS`。**新建源文件之后，第一件事是把它登记到构建系统。**

### 11.5 模板：同一个道理的延伸

工程里没有模板，但你以后一定会遇到。模板函数/类的定义**也必须放在头文件里**
（或者显式实例化），原因和 `inline` 完全相同：编译器需要看到定义才能为具体类型生成代码。
放到 `.cpp` 里会得到 `undefined reference`——症状和 HW3 一模一样。
这一条现在记住结论就行，不必现在深入。

> **工程里在哪见过它**：`CMakeLists.txt:11-16`、`tests/CMakeLists.txt:1-7`、
> 附录 A 的三份 `nm` 输出。

---

## 11b. 模板：知道有这回事就行

模板在战队代码里出现 **249 次**，但**大部分在库和底层工具里**
（`lib/arm_math/`、矩阵、滤波器）。业务代码里你基本是**调库**，
不是写库。所以这一节的目标很低：**看到不慌，知道去哪儿查。**

### 11b.1 一眼看懂就够

```cpp
template <typename T>
T maxOf(T a, T b) { return (a > b) ? a : b; }

maxOf(1, 2);         // 编译器按 int 生成一份
maxOf(1.0f, 2.0f);   // 编译器按 float 再生成一份
```

**一句话**：模板是"类型也是参数"，编译器按你用的类型各生成一份代码。
用得越多，编译出来的代码越大 —— 这是它在固件里要被克制使用的原因。

### 11b.2 你会看到的一种写法

```cpp
// wheel-legged/base/common/matrix.h:17（原样抄）
template <int n_row, int n_col>
class Matrix_f32 {
  ...
 protected:
  arm_matrix_instance_f32 inst_;
  float32_t data_[n_row][n_col];
```

**值也能当模板参数**，所以数组维度可以写成 `data_[n_row][n_col]`，
`Matrix_f32<6, 6>` 和 `Matrix_f32<6, 1>` 是两个不同的类型。

你要知道的只有两点：

1. **尖括号里的东西是编译期定死的**，所以不占运行期开销、也不用动态分配。
2. **维度对不上会编译不过**（`Matrix_f32<6,6>` 乘 `Matrix_f32<3,1>`），
   这是好事 —— 错误提前暴露了。

> **不用学怎么定义模板。** 你是调库的人：`Matrix_f32<6, 6> J;` 会用就行。
> 真到了要自己写模板的那天（多半是在驱动层或算法库），
> 那时候你已经有足够的 C++ 底子，看文档就会了。

### 11b.3 这些看到就跳过

```cpp
std::void_t<...>                       // SFINAE 的辅助工具
std::enable_if<...>                    // 条件启用某个重载
std::decay_t<...>                      // 类型退化
template<typename, typename = void>    // 偏特化的经典形状
```

真实代码里一共不到 10 处，都在底层工具库里。
**认得出来"这是高级技巧"就够了**，去找写得清楚的注释或文档，别硬读。

---

## 12. 嵌入式 C++ 的现实约束

这一节和前面不同：前半部分是**这个工程里可验证的事实**，后半部分是**真实固件工程的
通用约束**（工程里没有对应代码，但你必须知道）。

### 12.1 先看这个工程里没有什么

这个工程里**一处都没有**用到 `new` / `delete` / `try` / `catch` /
`std::vector` / `std::string`。在 IDE 里 `Ctrl+Shift+F` 搜这几个词就能确认。

全部 `std::` 用法只有三个名字（共 7 处调用），都在测试里：

```cpp
// tests/test_util.h:4-6
#include <cmath>
#include <cstdio>
#include <cstring>
// :23 std::fabs   :25 :27 :36 :38 :43 std::printf   :34 std::strcmp
```

这不是"作者不会用"，是刻意的选择。下面说明为什么。

### 12.2 不用异常（`-fno-exceptions`）

固件工程通常关掉异常：

- **代码体积**：异常要额外生成展开表（unwind table），一个 STM32F407 的 flash 只有
  1 MB，这份开销在小型工程里可以占百分之几到十几；
- **栈不可预测**：异常抛出时要沿调用栈展开，最坏情况的栈深度无法静态分析。
  机器人控制循环的栈是提前算好的，不能容忍这种不确定性；
- **中断里不能抛**：中断服务函数里抛异常是未定义行为；
- **其实也没人 catch**：控制代码里没有"抛出去让上层处理"的场景，到处 `try/catch`
  只是把错误藏起来。

关了异常之后，错误处理靠：**返回值 + 状态码 + 看门狗**。工程里的
`ClampState`（`app/arm.h:28`）就是这种风格——`update()` 返回一个状态，
调用者自己判断（`app/control.cpp:33`）。另一个例子是 `MotorFeedback::online`
（`app/arm.h:24`）：在线就 `true`，离线就 `false`，没有异常，没有可选值。
（顺带一提：`MotorFeedback` 这个共享类型在工程里目前还没有模块用到——全工程搜
`MotorFeedback` 只命中定义处。它是给后续模块预留的，也正好说明"共享类型集中在
`arm.h`"这个约定。）

### 12.3 不用 RTTI（`-fno-rtti`）

`dynamic_cast` 和 `typeid` 需要类型信息表。关掉之后：

- 二进制更小；
- 更重要的：**你不需要它**。多态在这个场景里通常用"一个虚函数 + 枚举标签"就够了，
  真的需要类型判断时，加一个 `type()` 虚函数返回 `enum class` 更省、更可控。

工程里连虚函数都没有（三个模块都是直接持有的对象：`app/control.cpp:18-19`），
这是更彻底的选择：**能在编译期定下来的东西，不要拖到运行期。**

### 12.4 慎用动态分配

`new` / `delete` / `std::vector` / `std::string` 都会在堆上分配。固件里不用它们的原因：

1. **堆碎片**：跑几个小时后，堆变成一堆小空洞，一个稍大的分配就失败。
   失败发生在比赛第 5 分钟，而你复现不了；
2. **分配时间不确定**：实时控制循环要求每周期耗时稳定，`malloc` 的最坏耗时不可控；
3. **失败没法处理**：关掉异常后 `new` 失败返回什么？`std::bad_alloc` 抛不出来，
   很多嵌入式实现直接 `abort`——在机器人上就是死机。

替代做法：

| 需求 | 主机上会用 | 固件里用 |
| --- | --- | --- |
| 固定长度数组 | `std::vector<T>` | `T arr[N]` / `std::array<T, N>` |
| 变长但上限已知 | `std::vector<T>` | 固定容量数组 + 一个 `size_t len` |
| 字符串 | `std::string` | `char buf[N]` + 长度约定 |
| 一大块共享缓冲 | `new[]` | 全局静态数组（`.bss`），启动时确定 |
| 多态对象集合 | `std::vector<std::unique_ptr<Base>>` | 每类一个固定数组，或对象池 |

工程里的做法是最简单的一档：**所有对象都是全局或栈上的值，容量都在编译期确定。**
`MotorMonitor g_joint_monitor;`（`app/control.cpp:18`）这种全局对象放在 `.bss`，
启动时由 C++ 运行时代码构造（因为成员都有 NSDMI，构造是常量级的，几乎无开销）。

### 12.5 那还能用什么

- **值语义 + 小函数**：`MotorData`、`ClampState` 这些类型按值传递、按值返回；
- **编译期常量**：`constexpr`（§5.3），不占 RAM；
- **模板**：编译期生成代码，运行期零开销（但会让 flash 变大，要用得克制）；
- **`std::array` / `std::span` / `std::clamp` 这类无分配的库设施**：见 §13.3。

### 12.6 `volatile` 与寄存器（通用经验）

嵌入式里 `volatile` 表示"这个值可能被外部改变，不要优化掉这次读"。
典型场景是硬件寄存器和中断里改的标志位：

```cpp
// 示意（不在 day0/project 里）
volatile uint32_t* const kCanStatus = reinterpret_cast<volatile uint32_t*>(0x40006400U);
while ((*kCanStatus & 0x1U) == 0U) { }    // 编译器不能把这个读操作优化掉
```

规矩：**只在必须的地方用 `volatile`**（寄存器、ISR 共享变量）。
给普通变量加 `volatile` 只会阻止优化，不会让它变线程安全。

### 12.7 中断上下文（通用经验）

中断服务函数（ISR）里能做的事：读寄存器、置标志、拷一小段数据。
不能做的事：`printf`、动态分配、长循环、等待、调用可能阻塞的函数。
主循环看到标志位再处理——工程里 `MotorMonitor::update`（`app/motor_monitor.cpp:15`）
这种"收到一帧反馈就更新一次"的函数，就适合由 CAN 接收回调调用；
而真正耗时的解算应该放在控制循环里。

> **工程里在哪见过它**：`app/arm.h:20-33`（状态码代替异常）、`app/control.cpp:18-19`
> （静态对象）、`tests/test_util.h:4-6`（唯一的 `std::` 用法）、`base/motor.h:6-13`
> （值类型）。

---

### 12.8 真实仓库里的 `new` 长什么样（这一节要更新你的判断）

§12.4 说"慎用动态分配"。**但"慎用"不等于"没有"** ——
战队自己的代码里 `new` / `delete` 出现 **305 次**。所以正确的说法是：

> **分配这件事本身不危险，"反复分配"和"在运行期分配"才危险。**

看真实用法。**第一种：构造时分配一次，之后再也不动。**

```cpp
// wheel-legged/base/common/kalman_filter.cpp:18（原样抄）
                           const float* Q, const float* R, const float* x0)
    : x_size_(x_size), u_size_(u_size), z_size_(z_size) {
  // prior estimated state vector x_hat, x(k|k)=x0
  data_.x_hat = new float[x_size_];
  MatrixInit(&mat_.x_hat, x_size_, 1, (float*)data_.x_hat);
  memcpy(data_.x_hat, x0, x_size_ * sizeof(float));
  // posterior estimated state vector x_minus, x(k|k-1)
  data_.x_minus = new float[x_size_];
  MatrixInit(&mat_.x_minus, x_size_, 1, (float*)data_.x_minus);
  // control vector u
  data_.u = new float[u_size_];
  MatrixInit(&mat_.u, u_size_, 1, (float*)data_.u);
  ...
```

为什么这样能接受：

- 分配发生在**构造函数**里，对象活多久、这块内存就活多久
- 全程只有**一次**分配，不产生碎片
- 尺寸 `x_size_` / `u_size_` 在构造时就定了，之后不变

同样的写法在 `filter.h:56`（`a_ = new float[order];`）、`lqr.cpp`、`matrix.cpp` 里都有。

**第二种：真正的运行期动态分配 —— 场景图。**

```cpp
// wheel-legged/app/client_ui.cpp:120（原样抄，省略了链式调用的后半段）
  // 电容条
  ui.add((new Rect("rc0", 2, TEAM_COLOR, 8, 700, 800 - 15, 700 + 500, 800 + 15))
             ->setPriority(3)
             ->setPriorityCalcFunc(relativeStaticPriRule)
             ->setStaticContent())
      .add((new Line("rc1", 2, color, 28, 700, 800, 700 + 500 * energy_percent,
                     800))
               ->setPriority(1)
```

这是裁判系统 UI 的图元：每种图元（`Rect` / `Line` / `FloatNum` / `Str`）
通过基类指针挂到一棵树上。**这是真·多态 + 真·运行期分配**，
而且它只在 UI 初始化时跑一次。

### 12.9 那到底什么时候可以 `new`

| 场景 | 能不能 | 为什么 |
| --- | --- | --- |
| 构造时分配、尺寸此时已定、之后不再动 | ✅ | 只发生一次，不产生碎片（§12.8 第一种） |
| 启动时按配置建一次对象树 | ✅ | 同上，`client_ui` 就是这种 |
| 运行期反复 `new` / `delete` | ❌ | 跑几小时后堆变成一堆空洞，失败发生在比赛第 5 分钟 |
| 控制循环里分配 | ❌ | 最坏耗时不可控，周期会飘 |
| 尺寸编译期就定得下来 | ❌ 用不着 | 静态数组更省、更快、可静态分析（§11b.2 的模板就是干这个的） |

**判断法**：问自己"这段代码在机器人跑起来的**第 10 分钟**还会执行吗？"
会 → 不能分配。只在开机时执行 → 可以。

> 这个改判很重要。原来那句"固件里不用堆"会让你第一次读到 `kalman_filter.cpp`
> 就困惑：到底是我理解错了，还是这代码有问题？
> **都不是** —— 是"不用堆"这个说法太粗了。

---

## 13. `std::`：容器与算法

### 13.1 `<cmath>` 还是 `<math.h>`

C++ 标准库把 C 的头文件重新包装了一遍，去掉 `.h` 并加 `c` 前缀：

| C | C++ | 区别 |
| --- | --- | --- |
| `<math.h>` | `<cmath>` | 函数放进 `std::` 命名空间（`std::fabs`），宏减少了 |
| `<stdio.h>` | `<cstdio>` | `std::printf` |
| `<string.h>` | `<cstring>` | `std::strcmp` |
| `<stdint.h>` | `<cstdint>` | `std::uint8_t`（通常同时提供全局 `uint8_t`） |

工程里测试用的是 `<cmath>` / `<cstdio>` / `<cstring>`（`tests/test_util.h:4-6`），
而 `app/arm.h:4` 用的是 `<cstdint>` 并直接用 `uint8_t`——这是实践中最常见的写法，
`<cstdint>` 的实现会同时把名字放进全局命名空间。

**新代码用带 `c` 前缀的版本。** 老代码里的 `<math.h>` 不是错，只是不够 C++。

### 13.2 这个工程为什么不用容器

理由在 §12.4。补一句：这个工程的"数据规模"全在编译期确定——
两个电机、一个夹爪、四个测试用例。用 `std::vector` 只会引入一个堆分配，
换来的是"运行时才知道有几个元素"的灵活性，而这里根本不需要。

### 13.3 主机侧测试可以用容器

测试代码跑在电脑上，不受固件约束。`tests/test_encoder.cpp:22-36` 的测试数据现在
写成了 C 数组：

```cpp
const float fwd_wrap[] = {355.0f, 359.0f, 3.0f, 7.0f};
testutil::check_near("forward across zero", run(fwd_wrap, 4), 12.0f, 0.01f);
```

用 `std::array` 会稍微好一点（能直接取到长度，不用手写 `4`）：

```cpp
// 示意（不在 day0/project 里，是主机的测试代码）
#include <array>
const std::array<float, 4> fwd_wrap{355.0f, 359.0f, 3.0f, 7.0f};
testutil::check_near("forward across zero", run(fwd_wrap.data(), fwd_wrap.size()), 12.0f, 0.01f);
```

注意 `std::array` 是**栈上**的固定数组，没有堆分配，所以它在固件里也是可以用的。

### 13.4 值得认识的几个（都不分配内存）

| 设施 | 干什么 | 头文件 | 固件里能用 |
| --- | --- | --- | --- |
| `std::array<T, N>` | 定长数组，能取 `size()`、能整体赋值 | `<array>` | 能 |
| `std::span<T>` | 一个指针 + 长度，看一段连续数据（C++20） | `<span>` | 能（C++20 起） |
| `std::clamp(v, lo, hi)` | 把值夹到区间里 | `<algorithm>` | 能 |
| `std::min` / `std::max` | 取小/大 | `<algorithm>` | 能 |
| `std::size` / `std::data` | 取 C 数组的长度/指针 | `<iterator>` | 能 |
| `std::vector` / `std::string` | 动态数组 / 字符串 | `<vector>` `<string>` | **不能**（堆分配） |
| `std::function` | 通用可调用对象 | `<functional>` | 慎用（可能堆分配） |

`std::clamp` 和工程里的 `clampf`（`base/math.h:15-19`）功能一样。
真实固件工程里仍然常见自己写一份，原因：工具链的 C++ 标准库版本可能很老
（Keil 的 armcc 长期停在 C++03/11）、`<algorithm>` 会拖进一堆头文件、
以及自己写的版本在调试时更容易单步进去。**知道有标准版本，也知道什么时候不用它**，
这就是分寸。

### 13.5 算法与 lambda 长什么样

```cpp
// 示意（不在 day0/project 里）
#include <algorithm>
#include <array>

const std::array<float, 6> kAngles{0.0f, 30.0f, 90.0f, 180.0f, 270.0f, 355.0f};
// 找一个"接近 180 度"的元素
auto it = std::find_if(kAngles.begin(), kAngles.end(),
                       [](float a) { return a > 179.0f && a < 181.0f; });
const bool found = (it != kAngles.end());
```

`[](float a) { ... }` 是 lambda，一个就地写的小函数。捕获列表 `[]` 空表示不捕获外部变量，
`[&]` 按引用捕获，`[=]` 按值捕获。**在中断和实时循环里避免 `[&]` 捕获局部变量**，
理由和 §6.5 一样：生命周期。

### 13.6 什么时候真的该用容器

主机侧工具、上位机、视觉算法、日志缓冲——这些跑在电脑上、元素个数运行期才知道的地方。
一句话判断：**这段代码会不会烧进 MCU？会，就别堆分配；不会，放心用。**

> **工程里在哪见过它**：`tests/test_util.h:4-6`、`:23`、`:25`、`:34`、
> `app/arm.h:4`、`base/math.h:15-19`。

---

## 14. `extern "C"`：C 和 C++ 混编

固件工程必然是混编的：**HAL 是 C，业务代码是 C++**。
这一节讲清楚它们怎么接上 —— 你不需要写，但需要看懂。

### 14.1 它解决什么问题

C++ 编译器会给函数名加料。同一个 `void led_on()`，在 `nm` 里可能变成
`_Z6led_onv`（§11.3 那张符号表里见过这种名字）。
C 编译器不会加料，它就叫 `led_on`。

于是：**C 文件里调用一个 C++ 实现的函数，链接器找不到那个名字** ——
一个和 §3.5 一模一样的 `undefined reference`，只是原因不同。

`extern "C"` 就是在说："这个名字按 C 的规则来，别加料。"

### 14.2 真实仓库里长什么样

```cpp
// dual-arm/MasterArm/interface/callback.h:9（原样抄，省略了中间的声明）
#ifndef CALLBACK_H
#define CALLBACK_H

#ifdef __cplusplus
extern "C" {
#endif

#include "usart.h"

// UART idle callback. Called in stm32f4xx_it.c USARTx_IRQHandler()
// UART空闲中断处理，在stm32f4xx_it.c的USARTx_IRQHandler()函数中调用
void User_UART_IdleHandler(UART_HandleTypeDef* huart);

#ifdef __cplusplus
}
#endif

#endif  // CALLBACK_H
```

**为什么长这样**：中断服务函数写在 C 文件里（`stm32f4xx_it.c`），
实现在 C++ 文件里（`callback.cpp`）。中间这个头文件是两边的接缝。

三个值得注意的地方：

1. **`#ifdef __cplusplus` 的包裹**：只有 C++ 编译器看到 `extern "C" {`，
   C 编译器看到的是空行。**同一个头文件两边都能 include** —— 这是关键。
2. **它连 `#include "usart.h"` 都包进去了**。因为 `usart.h` 是 HAL 的
   C 头文件，从 C++ 里 include 它也要按 C 规则处理。
3. **每个函数注释都写了"谁调用它"**（`Called in stm32f4xx_it.c ...`）。
   这是这套代码里最值得学的习惯：中断回调散落各处，
   不写清楚调用点，半年后没人找得到。

### 14.3 你该记住的

| | |
| --- | --- |
| **在哪见到它** | 所有 `interface/` 下的头文件 —— 那一层就是 C 和 C++ 的接缝 |
| **看到怎么办** | 知道"这里在给 C 代码提供入口"，具体函数照常读 |
| **要写吗** | 现在不用。等你在 `interface/` 里加中断回调时，照着旁边的抄 |
| **写错了会怎样** | `undefined reference to led_on`（而不是 `_Z6led_onv`）—— 名字对不上 |

> 你现在这个练习工程没有 `interface/` 这一层（它依赖具体的 HAL）。
> 但你以后一定会在这一层写代码 —— 那时回来看看这一节就够。

---

## 15. 从讲义回到练习

`day0/cpp/` 里留了四组 `TODO(cppN)`。每组对应本文的哪几节：

| 练习 | 文件 | 你要做的 | 用到的知识 |
| --- | --- | --- | --- |
| **cpp1** | `base/common/math.cpp` | 实现 `limit` / `loopLimit` / `degNormalize180` / `isNanOrInf` | §3 声明与定义、§4 inline、§6.7（真实仓库的同一段代码）、§6c.4 |
| **cpp2** | `base/motor/motor.cpp` | `Motor::setTorque`：**先限幅、再窄化** | **§7b.1–7b.3**（参数怎么传）、§6c.3（类型转换） |
| **cpp3** | `app/chassis.cpp` | `modeName` 与 `Chassis::update` 状态机 | §8.3 `switch` 覆盖枚举、§6b（指针数组）、§9 |
| **cpp4** | `base/motor/dji_motor_driver.cpp` | 解析 / 打包 C620 的 8 字节报文 | **§6c** 全部、§6c.5 定长类型、§6c.6 结构体布局 |

四组的顺序是有依赖的：`cpp3` 的 `Chassis::update` 要调 `cpp2` 写好的
`Motor::setTorque`。所以按 cpp1 → cpp2 → cpp3 做，`cpp4` 可以插在任何时候。

**做完怎么知道对了** —— 每个练习都有对应的单元测试，在工程根目录下：

```bash
python tools/build.py          # 构建 + 跑测试
python tools/grade.py cpp1 .   # 用验收工具自查（和老师用的是同一份代码）
```

`cpp1` 一开始会**编译不过**，报的是 `undefined reference to math::limit(...)`。
这不是环境坏了 —— 是 `math.cpp` 里还没有实现。这条报错本身就是第一课（§3.5）。

---

### 15.1 另一条线：Git 模块的 HW1–HW5

`day0/project/` 里那套工程是 **Git 模块**用的，和 C++ 模块相互独立。
但概念是同一批，碰到了可以对照：

| 作业 | 你会做的事 | 相关节 |
| --- | --- | --- |
| HW2 | 修 `base/math.h` 里的编码器回绕 bug | §6.7（真实仓库的同一段实现） |
| HW3 | 制造并修复一个链接错误 | §3.5、§11.2、§11.4 |
| HW5 | 提交改动、处理合并冲突 | §8.4（枚举是"追加点"）、§10 |

---

## 16. 自测题

做完再看 §17。凭记忆答，不要翻前面。

1. `app/control.h` 里只有 `void controlInit();` 这样的声明，没有函数体。
   为什么编译 `app/control.cpp` 时编译器不报错？
2. 把 `base/math.h:8` 的 `inline` 去掉、只留函数定义，什么情况下能编过，
   什么情况下会报错？报的是什么错？
3. HW3 里 `undefined reference to 'wrap_angle_deg(float)'` 是哪个阶段报的？
   为什么在那之前 `libday0_core.a` 能成功生成？
4. `app/control.cpp:18` 的 `g_joint_monitor` 放在匿名命名空间里，
   和放在全局作用域有什么区别？`nm` 输出里怎么区分？
5. `app/clamp.h:18` 的 `static constexpr float kResistThreshold` 里，
   `static` 和 `constexpr` 各起什么作用？
6. `Clamp::isCalibrating()`（`app/clamp.h:11`）没有写 `inline`，
   为什么可以被多个 TU 包含而不冲突？
7. `const MotorData& data() const` 这一行里的两个 `const` 分别修饰什么？各有什么作用？
8. `MotorData data_{};` 和 `MotorData data_;` 有什么区别？为什么工程里选前者？
9. `enum Mode_e` 和 `enum class ClampState` 有什么实际区别？各举一处工程里的用法。
10. `tests/test_clamp.cpp:9` 的 `name()` 函数为什么可以不写 `default` 分支？
    不写 `default` 有什么好处？
11. `tests/test_util.h:12` 的 `static int n = 0;` 在 `inline` 函数里，
    是每个 TU 一份还是全程序一份？符号表里长什么样？
12. 为什么 `using namespace std;` 不应该写在头文件里？
13. `#include "app/arm.h"` 能编译通过，是谁告诉编译器去工程根目录找的？
    如果少了那一行 CMake 配置，会是什么症状？
14. `base/math.h` 用的是 2 空格缩进，而 `.clang-format:32` 写着 `IndentWidth: 4`。
    这两件事同时成立说明了什么？（提示：想想 HW4）
15. 这个工程里为什么一处 `new`、`try`、`std::vector` 都没有？
    分别给出至少一条嵌入式上的理由。
16. `app/control.cpp:34-35` 的 `(void)state;` 和 `(void)ctrl_params::kDefaultClampSpeed;`
    在干什么？不写会怎样？
17. `<cmath>` 和 `<math.h>` 有什么区别？这个工程里用的是哪个？
18. 如果 `app/arm.h` 忘了写 include guard，而它被同一个 TU 包含两次，
    报的是编译错误还是链接错误？错误信息大概是什么样？
19. `void update(float a, float b, float c)` 为什么按值传参，
    而 `const MotorData& data()` 为什么返回 `const` 引用？
20. `libday0_core.a` 是什么？它和 `.o` 文件是什么关系？
    为什么 `test_encoder` 和 `test_clamp` 都要链接它？

---

## 17. 自测题答案

**1.** 编译器一次只处理一个 TU（`app/control.cpp` 加上它包含的头文件），
它不读别的 `.cpp`，所以无从判断"别处有没有实现"。看到声明，它就认为"这个函数存在"，
调用写对了就放行。判断"到底有没有定义"是链接器的活。（§1.3、§3.5）

**2.** 只有一个 TU 包含 `base/math.h` 时能编过（甚至看不出 `inline` 有什么用）；
两个以上 TU 包含时会重复定义，链接阶段报
`multiple definition of 'deg_normalize_180(float)'`。
`inline` 的语义就是"允许多份相同定义，链接器合并成一份"。（§4.1）

**3.** 链接阶段报的，来自 `ld`（`collect2: error: ld returned 1 exit status`）。
`.a` 只是 `.o` 的打包，`ar` 不解析符号引用，所以能生成；
真正解析符号是在链接**可执行文件**（`test_encoder`）的时候。（§3.5、§11.2）

**4.** 匿名命名空间的对象具有内部链接，只有本 TU 能访问；放在全局作用域则是外部链接，
别的 TU 用 `extern` 就能访问，也更容易撞名。
判断办法：在另一个 `.cpp` 里试着引用它 —— 匿名命名空间的东西链接不上，
全局的能链上。（§9.3）

**5.** `static`：这个常量属于类、不属于对象，所有对象共用一份，`sizeof(Clamp)` 不含它。
`constexpr`：编译期常量，能直接编进指令、不占 RAM。
C++17 起类内 `static constexpr` 不需要在 `.cpp` 里再定义一次。（§5.3、§10.3）

**6.** 定义在类体内部的成员函数**隐含 `inline`**。
它在多个 TU 里各有一份定义，链接器合并成一份。（§4.5）

**7.** 返回类型里的 `const` 修饰"通过这个引用能做什么"——调用者只能读，不能改内部状态。
参数列表后面的 `const` 修饰这个成员函数本身——它承诺不修改对象，因此可以被
`const` 对象调用。（§6.2）

**8.** `MotorData data_{};` 用空列表初始化成员：每个成员按默认成员初始化器（NSDMI）处理，
一定会被初始化。`MotorData data_;` 是默认初始化：**如果某个成员哪天被去掉了 NSDMI，
它就是不确定值**。工程里选前者是为了"任何路径下都归零"。（§7.4）

**9.** `enum class` 的枚举名不会泄漏到外层作用域，必须写 `ClampState::kBlocked`；
也不会隐式转换成 `int`。`enum Mode_e` 的枚举名泄漏（`FOLD` 是全局名字），
而且能隐式参与整数运算。工程里 `app/control.cpp:20` 用 `Mode_e::FOLD`，
`app/clamp.cpp:17` 用 `ClampState::kBlocked`。
两者都指定了底层类型 `: uint8_t`。（§8.1、§8.2）

**10.** 因为枚举的所有取值都被 `case` 覆盖了，末尾还有一个兜底 `return "?";`。
不写 `default` 是为了让 `-Wall` 下的 `-Wswitch` 警告能提醒你"新增枚举值后忘了处理"。
写了 `default` 反而会吞掉这个提醒。（§8.3）

**11.** 全程序一份。C++ 标准规定 `inline` 函数里的函数级 `static` 变量是同一个实体。
符号表里是 `u testutil::checks()::n`（`u` = unique global symbol）。（§10.2）

**12.** 头文件会被很多 TU 包含，`using namespace std;` 会把这些 TU 全部拖进
`std` 的成百上千个名字里，`count`、`size` 这类常见名字随时可能冲突，
而且冲突报错极难读。头文件里写全名 `std::`。（§9.5）

**13.** `CMakeLists.txt:16` 的 `target_include_directories(... PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})`
把它加进了 `-I` 搜索路径（可在 `build/CMakeFiles/day0_core.dir/flags.make` 里看到）。
少了它，报错是 `fatal error: app/arm.h: No such file or directory`——
**编译**错误，不是链接错误。（§1.3、§2.1）

**14.** 工程的风格配置和实际代码可以长期不一致。`.clang-format` 是从真实仓库抄来的、
没有被统一执行过。HW4 就是让你只对 `base/` 执行一次，并且**不要**顺手格式化整个仓库。
（§2.5，HW4 正文）

**15.** 异常：代码体积（展开表）、栈深度不可静态分析、ISR 里不能抛。
RTTI：类型信息表占空间，而且这个场景用状态码更合适。
动态分配：堆碎片、分配耗时不确定、关掉异常后分配失败没法处理。
工程里用 `ClampState`、`MotorFeedback::online` 这类状态值表达"出错"，
对象全部是全局或栈上的值。（§12.2–§12.4）

**16.** 显式告诉编译器"我知道这个变量没用，别警告"。
不写的话，开了 `-Wunused-variable`（`-Wall` 的一部分）会报
`unused variable 'state'`。骨架代码和"为了调试先看一眼"的场景里很常见。（§5.1）

**17.** `<cmath>` 是 C++ 版本的 `<math.h>`：函数放进 `std::` 命名空间，宏更少。
工程里测试用的是 `<cmath>` / `<cstdio>` / `<cstring>`（`tests/test_util.h:4-6`），
`app/arm.h:4` 用的是 `<cstdint>`。（§13.1）

**18.** 编译错误，因为问题发生在同一个 TU 内部。
信息形如 `error: multiple definition of 'enum Mode_e'` 加一行
`note: previous definition here`。带上 guard 后头文件在一次编译里只被展开一次。（§2.2）

**19.** `float` 只有 4 字节，按值传比传引用更快，也不用担心函数里改到外面。
`MotorData` 有 6 个 `float`，按值返回要拷贝，而且 `data()` 的语义是
"看内部真实状态"，所以返回 `const` 引用：不拷贝，同时禁止调用者改内部。（§6.2、§6.3）

**20.** `.a` 是静态库，是多个 `.o` 的归档包（`ar t build/libday0_core.a` 列出
`control.cpp.o`、`motor_monitor.cpp.o`、`clamp.cpp.o`）。
链接时只挑被用到的目标文件。两个测试都用到 `MotorMonitor` / `Clamp`，
所以都链接它（`tests/CMakeLists.txt:2`、`:6`）。（§11.1、§11.2）

---

## 附录 A · 本机实测记录（**选读**）

> **这一节不用读。** 它是正文里那些结论的原始证据，用的是 `nm` / `ar` 这类
> 命令行工具 —— **Windows 上默认没有，装了 MinGW-w64 或 Git Bash 才会有。**
>
> 正文已经把这些工具的输出翻译成了"你会看到什么报错、该查什么"，
> 不需要你自己跑一遍。只有两种情况值得翻这里：
> ① 你想确认某个结论是不是真的；② 你想学怎么用这些工具（以后在 Linux 上会用得到）。

环境：`g++ (Ubuntu 11.4.0-1ubuntu1~22.04.3) 11.4.0`，`cmake version 3.22.1`。
命令都在 `day0/project` 下执行。

### A.1 静态库和它的成员

```bash
$ ar t build/libday0_core.a
control.cpp.o
motor_monitor.cpp.o
clamp.cpp.o
```

### A.2 `control.cpp.o` 的符号表

```bash
$ nm -C build/CMakeFiles/day0_core.dir/app/control.cpp.o
0000000000000000 T controlInit()
0000000000000049 T controlLoop()
0000000000000078 T currentMode()
0000000000000004 r ctrl_params::kJointRate
000000000000000c r ctrl_params::kMouseVisionRate
0000000000000008 r ctrl_params::kChassisRotateRate
0000000000000000 r ctrl_params::kDefaultClampSpeed
0000000000000000 b (anonymous namespace)::g_joint_monitor
000000000000001a b (anonymous namespace)::g_mode
0000000000000018 b (anonymous namespace)::g_clamp
                 U MotorMonitor::reset(float)
                 U Clamp::endCalibration()
                 U Clamp::beginCalibration()
                 U Clamp::update(float, float)
```

### A.3 `inline` 的符号是弱符号

```bash
$ nm -C build/CMakeFiles/day0_core.dir/app/motor_monitor.cpp.o
0000000000000000 W deg_normalize_180(float)
000000000000005c T MotorMonitor::reset(float)
0000000000000000 T MotorMonitor::reset()
00000000000000da T MotorMonitor::update(float, float, float)
```

### A.4 测试目标文件：类内成员函数与函数级 static

```bash
$ nm -C tests/CMakeFiles/test_encoder.dir/test_encoder.cpp.o
00000000000000d7 T main
                 U printf
                 U __stack_chk_fail
0000000000000000 t (anonymous namespace)::run(float const*, int)
                 U MotorMonitor::reset(float)
                 U MotorMonitor::update(float, float, float)
0000000000000000 W testutil::check_near(char const*, float, float, float)
0000000000000000 W testutil::checks()
0000000000000000 W testutil::report(char const*)
0000000000000000 W testutil::failures()
0000000000000000 W MotorMonitor::data() const
0000000000000000 W std::fabs(float)
0000000000000000 u testutil::checks()::n
0000000000000000 u testutil::failures()::n
```

### A.5 头文件里写普通函数定义 → 重复定义

三个文件：`hdr.h`（里面是 `float gain(float x) { return x * 2.0f; }`，带 include guard）、
`a.cpp`、`b.cpp` 都包含它。

```bash
$ g++ -std=c++17 -c a.cpp -o a.o && g++ -std=c++17 -c b.cpp -o b.o && g++ a.o b.o -o ab
/usr/bin/ld: b.o: in function `gain(float)':
b.cpp:(.text+0x0): multiple definition of `gain(float)'; a.o:a.cpp:(.text+0x0): first defined here
/usr/bin/ld: .../Scrt1.o: in function `_start':
(.text+0x1b): undefined reference to `main'
collect2: error: ld returned 1 exit status
```

（后两行是因为这个实验没有 `main`，和重复定义无关。）

### A.6 缺 include guard

```bash
$ g++ -std=c++17 -fsyntax-only dbl3.cpp
In file included from dbl3.cpp:2:
noguard.h:2:6: error: multiple definition of 'enum Mode_e'
    2 | enum Mode_e : uint8_t { FOLD, CRUISE };
      |      ^~~~~~
In file included from dbl3.cpp:1:
noguard.h:2:6: note: previous definition here
```

### A.7 HW3 复现：`undefined reference`

把 `base/math.h` 的实现换成 `float wrap_angle_deg(float deg);`，
并把 `app/motor_monitor.cpp:17` 的调用点改名之后：

```bash
$ cmake --build build
[ 12%] Building CXX object CMakeFiles/day0_core.dir/app/control.cpp.o
[ 25%] Building CXX object CMakeFiles/day0_core.dir/app/motor_monitor.cpp.o
[ 37%] Building CXX object CMakeFiles/day0_core.dir/app/clamp.cpp.o
[ 50%] Linking CXX static library libday0_core.a
[ 50%] Built target day0_core
[ 62%] Building CXX object CMakeFiles/test_encoder.dir/test_encoder.cpp.o
[ 75%] Linking CXX executable test_encoder
/usr/bin/ld: ../libday0_core.a(motor_monitor.cpp.o): in function `MotorMonitor::update(float, float, float)':
app/motor_monitor.cpp:17: undefined reference to `wrap_angle_deg(float)'
collect2: error: ld returned 1 exit status
```

修复前/后的符号对比：

```bash
$ nm -C build/libday0_core.a | grep wrap
                 U wrap_angle_deg(float)      # 只有声明
0000000000000000 T wrap_angle_deg(float)      # 补上实现之后
```

声明-only 的 TU 编译仍然通过：

```bash
$ g++ -std=c++17 -I. -fsyntax-only app/motor_monitor.cpp
$ echo $?
0
```

### A.8 漏 `case` 的警告

```bash
$ g++ -std=c++17 -Wall -fsyntax-only sw.cpp      # switch 里少了 kHolding
sw.cpp: In function 'const char* name(ClampState)':
sw.cpp:3:10: warning: enumeration value 'kHolding' not handled in switch [-Wswitch]
```

---

## 附录 B · 术语对照

| 英文 | 中文 | 一句话 |
| --- | --- | --- |
| translation unit (TU) | 编译单元 | 一个 `.cpp` 加它包含的所有头文件 |
| declaration | 声明 | 告诉编译器"有这么个东西" |
| definition | 定义 | 真的给出实体（函数体、存储） |
| ODR | 单一定义规则 | 函数/变量全程序一份；类型可多份但必须逐字相同 |
| inline | 内联 | 主要语义：允许多 TU 各有一份相同定义 |
| linkage | 链接性 | 这个名字能不能被别的 TU 看见 |
| internal linkage | 内部链接 | 只有本 TU 可见（匿名命名空间、`static`） |
| symbol | 符号 | 链接器眼里的名字，`nm` 能看 |
| mangling | 名字修饰 | C++ 把参数类型编进符号名；`extern "C"` 关掉它 |
| NSDMI | 默认成员初始化器 | 成员声明处的 `= 0.0f` |
| aggregate | 聚合类型 | 没有用户构造函数、成员全公开，可以 `{}` 列表初始化 |
| scoped enum | 限定作用域枚举 | `enum class`，名字不泄漏、不隐式转整数 |
| RTTI | 运行期类型信息 | `dynamic_cast` / `typeid` 需要的表；固件里关掉 |
| static library | 静态库 | `.a`，`.o` 的归档包，链接时按需取用 |
