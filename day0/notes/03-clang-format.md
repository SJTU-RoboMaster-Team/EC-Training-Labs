# 录播 03 · clang-format
<!-- ⚠️ 这个文件由 lab/sync_grader.py 从 Tools/03-clang-format.md 复制而来。
     要改请改那份，然后重新同步 —— 不要直接改这里。 -->

> ℹ️ **这段录播还没发布。** 下面的 `🎬 视频 0X-Y · 00:00` 是分段占位符 ——
> 时间戳会在录像上线后回填。**在此之前，本文是自足的**：每一段都写了
> 「看什么、看到什么算过」，照着文字和截图走完是一样的。

| 项目 | 内容 |
| --- | --- |
| **这节讲什么** | 格式化到底解决什么问题；工程里那份 `.clang-format` 逐条解释；**怎么让 IDE 读工程配置而不是它自己的规则**；格式化范围的纪律（为什么不能顺手把整个仓库格式化）；命令行只用一句 |
| **多长时间** | 约 16 min，分 5 段（`03-1` ~ `03-5`），每段 2–5 min |
| **对应哪份作业** | **HW4（格式化）——整节都是它的前置**；HW5 里"格式化改动要单独一个 commit"这条规则的出处也是 `03-4` |

> 这节是三段录播里最短的，但 **`03-4` 是唯一一段"做错了会有真实后果"的内容**。
> 配置怎么填，忘了可以回来看；范围开大了，你要在 HW5 的合并里自己收拾。

**分段表**（录的时候按这个切）：

| 段 | 标题 | 目标时长 |
| --- | --- | --- |
| 03-1 | 它解决什么问题 | 3 min |
| 03-2 | 逐条读 `.clang-format` | 5 min |
| 03-3 | 在 IDE 里用它：必须让 IDE 读工程配置 | 3 min |
| 03-4 | 格式化范围的纪律 | 3 min |
| 03-5 | 命令行：提一句就够 | 2 min |

---

## 03-1 · 它解决什么问题

> 🎬 视频 03-1 · 00:00

### 问题不是"谁写得好看"

一个新人在仓库里写：

```cpp
if(speed>100){pid.kp=1.5;}
```

十分钟后另一个人写了：

```cpp
if (speed > 100)
{
    pid.kp = 1.5;
}
```

两个人谁都没错。但如果这类差异遍布整个文件，会产生三件事：

| 后果 | 具体是什么 |
| --- | --- |
| **review 变成吵架** | 有人开始评论"这里少个空格"，真正该看的逻辑改动没人看 |
| **diff 里全是噪音** | 你把 `{` 从下一行挪到同一行，`git diff` 就整块标红，别人看不出你到底改了什么 |
| **工具对不上** | 编辑器各自自动缩进，你一保存别人就要处理一堆假改动 |

**clang-format 做的事只有一件：把"排版"这个决定从人手里拿走，交给一份配置文件。**
写代码的人不用再想缩进几个空格、大括号放哪，机器每次都会给出同样的结果。

> 这就是为什么这类工具叫 **formatter** 而不是 **linter**：
> linter 告诉你"这里有可疑的地方"，formatter 直接改。
> 争议不在"要不要好看"，在**统一**——**统一之后，diff 里剩下的就都是真实改动了。**

### 我们这个工程的约定在哪

```text
EC-Training-Labs/day0/project/.clang-format
```

44 行 YAML。**它在工程根目录，所以整个 `project/` 目录下的 C/C++ 文件都归它管**
（`.clang-format` 的作用范围是"它所在的目录 + 所有子目录"）。

> ### 一个真实情况：团队仓库里 `.clang-format` 不止一份
>
> 我们三个仓库的去重历史里，一共出现过 **18 个不同的 `.clang-format` 文件**——
> 根目录一份、`engineer/.config/` 一份、`controller/.config/` 一份、
> 各个子模块目录里还有各自的。
>
> 这不是混乱，是现实：**不同年代的代码、不同的人接手，格式约定是分区域演化的。**
> 记住这一点，`03-4` 里"为什么不能顺手格式化整个仓库"就有了具体的理由——
> **你根本不知道那个目录里现在该用哪份约定。**

### 你现在看到的代码，其实不符合这份配置

打开 `base/math.h` 看一眼：

```cpp
inline float clampf(float v, float lo, float hi) {
  if (v < lo) return lo;
  if (v > hi) return hi;
  return v;
}
```

缩进是 **2 个空格**（这是 clang-format 的 LLVM 默认值），
而 `.clang-format` 里写的是 `IndentWidth: 4`；而且 `if (v < lo) return lo;`
这种一行两条语句的写法，在配置里是被明确禁止的。

**这就是真实项目的常态**：配置早就定好了，只是没人统一跑过一遍。
HW4 就是让这件事第一次发生——而且**只发生在一个目录里**。

**你应该看到什么**：把这两个文件并排打开看一眼——

```text
base/math.h        里的缩进是 2 个空格
.clang-format      里写的是 IndentWidth: 4
```

**两个对不上，这就是 HW4 要处理的东西。** 顺便在项目树里点一下
`app/`、`tests/`、`mcu/`：那些目录里的代码你从头到尾没看过，
它们的格式问题**不是你的活**（`03-4` 会解释为什么）。

### 如果没有

| 你的画面 | 原因 | 怎么办 |
| --- | --- | --- |
| 在 `day0/project/` 下用 `ls` 看不到 `.clang-format` | 以 `.` 开头的文件默认不显示 | 用 `ls -a`，或者在 CLion 的项目树里找（它会显示） |
| `base/math.h` 已经是 4 空格缩进 | 别人已经格式化过了 | 正常。HW4 仍然要你按自己的范围跑一遍并把范围限定在 `base/` |
| 找不到 `.clang-format` 这个文件 | 你在错误的目录 | 确认当前目录是 `EC-Training-Labs/day0/project/`；`git status` 看一眼它是不是被谁删了 |

---

## 03-2 · 逐条读 `.clang-format`

> 🎬 视频 03-2 · 00:00

**做什么**：把 `day0/project/.clang-format` 从头到尾读一遍，
每条说清"它管什么"、"我们选了什么"、"为什么"。

### 文件本身

```yaml
# Generated from CLion C/C++ Code Style settings
---
Language: Cpp
BasedOnStyle: LLVM
...
```

两个细节：

- 第一行说明它是 **CLion 导出**的（**Settings → Editor → Code Style → C/C++** →
  齿轮图标 → **Export → .clang-format File**）。
  所以"IDE 里的设置"和"仓库里的文件"可以互相导出——
  **但只有仓库里那份算数**，个人 IDE 里的设置别人看不到。
- `---` 是 YAML 的分隔符，clang-format 用它标记文档开头。没有也能工作，但标准写法是留着。

### 一条一条来

#### 基座

| 选项 | 我们的值 | 说清楚 |
| --- | --- | --- |
| `Language` | `Cpp` | 这份配置只作用于 C/C++ 文件，别的语言不受影响 |
| `BasedOnStyle` | `LLVM` | **基座**。clang-format 内置五套风格（LLVM / Google / Chromium / Mozilla / WebKit），不写 `BasedOnStyle` 的话，**没被显式覆盖的上百个选项取什么值是不确定的**。选了 LLVM 就是"以 LLVM 为底，下面这些改掉"。LLVM 的默认缩进是 2 空格，所以下面必须显式改成 4 |

#### 缩进与宽度

| 选项 | 我们的值 | 为什么 |
| --- | --- | --- |
| `IndentWidth` | `4` | 战队老代码都是 4 空格。选 4 是为了**让格式化后的代码和老代码长得一样**——如果选 2，第一次格式化会把所有文件的每一行都改一遍 |
| `TabWidth` | `4` | 如果有人用了 Tab，一个 Tab 按 4 列显示。**不要真的用 Tab**，`UseTab` 没开，clang-format 只输出空格 |
| `ColumnLimit` | `120` | 一行最多 120 字符。不用 80 是因为嵌入式代码的函数名和类型名长（`deg_normalize_180`、`MotorFeedback`、`HAL_GPIO_Init`），80 列会把一行挤成三行，反而难读。120 差不多是一个 1080p 屏幕两边都开面板之后还能完整显示的长度 |
| `MaxEmptyLinesToKeep` | `2` | 连续空行最多留 2 行。有人喜欢空 5 行分段，格式化后会被压成 2 行 |
| `InsertNewlineAtEOF` | `true` | **文件末尾必须有一个换行符。** 没有的话 `git diff` 最后一行会显示 `\ No newline at end of file`，而且和别人改动最后一行时必然冲突。这是一条"一次配好、永不操心"的规则 |

#### 大括号与类

| 选项 | 我们的值 | 为什么 |
| --- | --- | --- |
| `BreakBeforeBraces` | `Attach` | **1TBS 风格**：`{` 跟在 `if` / `for` / 函数签名的同一行，不另起一行。另一种常见风格是 `Allman`（大括号另起一行），Keil 的老代码里两种都有——**选 `Attach` 是因为它省行**，一屏能多看好几行代码 |
| `AccessModifierOffset` | `-4` | 和 `IndentWidth: 4` 配套：类体缩进 4 格，`public:` / `private:` **往回退 4 格**，于是访问修饰符和 `class` 关键字对齐。这样扫一眼就能看到类的分段 |
| `IndentCaseBlocks` | `true` | `switch` 里 `case` 下面的代码块整体缩进，读起来和别的块一致 |
| `NamespaceIndentation` | `All` | 命名空间里的内容**缩进**。LLVM 默认是 `None`（命名空间内容不缩进），但工程里 `namespace ctrl_params { ... }` 的内容明显是缩进的——**跟老代码一致**，避免第一次格式化时整块重排 |

#### 一行里只放一件事（这几条要一起看）

```yaml
# 严禁缩写在一行，保障 Debug 断点精度
AllowShortBlocksOnASingleLine: Empty
AllowShortFunctionsOnASingleLine: Empty
AllowShortIfStatementsOnASingleLine: Never
AllowShortLoopsOnASingleLine: false
AllowShortCaseLabelsOnASingleLine: false
```

**这五条是同一个决定**：不准把"多条语句"压缩到一行。逐个看：

| 选项 | 值 | 它的意思是 |
| --- | --- | --- |
| `AllowShortIfStatementsOnASingleLine` | `Never` | `if (x) return;` 必须拆成两行 |
| `AllowShortLoopsOnASingleLine` | `false` | `while (deg > 180) deg -= 360;` 必须拆成两行 |
| `AllowShortBlocksOnASingleLine` | `Empty` | 只有**空的** `{}` 能留在一行。`if (x) { do(); }` 会被拆开 |
| `AllowShortFunctionsOnASingleLine` | `Empty` | 同上，只有空函数体（`void f() {}`）能留在一行 |
| `AllowShortCaseLabelsOnASingleLine` | `false` | `case 1: return 2;` 要拆成两行 |

### 为什么 `Never` 是必须的：断点精度

拿工程里真实的那两行举例。格式化之前：

```cpp
inline float clampf(float v, float lo, float hi) {
  if (v < lo) return lo;
  if (v > hi) return hi;
  return v;
}
```

格式化之后（`IndentWidth: 4` + `Never`）：

```cpp
inline float clampf(float v, float lo, float hi) {
    if (v < lo)
        return lo;
    if (v > hi)
        return hi;
    return v;
}
```

**这一行被拆开，对功能没有任何影响——但对你调试影响很大。**

调试器是**按行号**设断点的，一行对应一个可停的位置。压缩写法下这一行里有两条语句：

```text
if (v < lo) return lo;
└─────┬────┘ └───┬───┘
  判断条件      真的要执行的动作
```

具体会发生什么：

| 你想做的事 | 压缩写法下 | 拆开之后 |
| --- | --- | --- |
| 在"真的执行了 return"这一下停下来 | 做不到——断点只能打在这一行，条件为假时也会停 | 断点打在 `return lo;` 上，只有真的走到才停 |
| 单步进去看 `lo` 的值 | 单步会直接跳到下一行（整行当成一步） | `F7`/`F8` 的粒度是"判断"和"返回"两步，看得清 |
| 编译器优化之后断点还准不准 | 更不准：这一行的两条语句可能被合并成一条指令 | 一行一条语句，映射关系稳定 |

**所以这条注释写的是"保障 Debug 断点精度"，不是"为了好看"。**
它对应讲义 `01-5` 里的另一半：Keil 里调试要关优化（`-O0`），
源码这边要一行一条语句。**两边都做到，断点才真的落在你想停的那一行。**

> 顺带说一个"配置过时了"的信号：
> 新一点的 clang-format 里 `AlwaysBreakTemplateDeclarations: Yes` 的 `Yes`
> 已经被 `MultiLine` 取代（`Yes` 仍然被接受，所以不用改）。
> 你在别的地方看到这种"文档里查不到的写法"，先别急着改——
> **能通过 `clang-format --dry-run -Werror` 的配置就是有效配置。**

#### 对齐类（全部关掉）

```yaml
AlignConsecutiveAssignments: false
AlignConsecutiveDeclarations: false
AlignOperands: false
AlignTrailingComments: true
```

前三个**故意关掉**，理由是同一件事：**对齐会产生大 diff。**

如果开了 `AlignConsecutiveAssignments`，一段赋值会变成：

```cpp
int  a      = 1;
int  longer = 2;
```

看起来很整齐。但**你改一个变量名，整块的等号位置都要重排**——
`git diff` 里就是十几行无关改动。在多人协作的仓库里，
这种"整齐"换来的代价比它带来的收益大。

`AlignTrailingComments: true` 留着，因为行尾注释不会因为别人改代码而重排。

#### 头文件排序

```yaml
IncludeCategories:
  - Regex: '^<.*'
    Priority: 1
  - Regex: '^".*'
    Priority: 2
  - Regex: '.*'
    Priority: 3
IncludeIsMainRegex: '([-_](test|unittest))?$'
```

排序规则，一眼能看懂：

| 优先级 | 匹配什么 | 例子 |
| --- | --- | --- |
| 1 | `<...>` 系统头 | `#include <cstdint>` |
| 2 | `"..."` 工程头 | `#include "app/control.h"` |
| 3 | 其它 | 少数带全路径的写法 |

工程里 `app/control.cpp` 的开头就是排好的：

```cpp
#include "app/control.h"

#include "app/clamp.h"
#include "app/motor_monitor.h"
```

`IncludeIsMainRegex` 管的是"这一组算不算主头文件"：
允许 `foo.cpp` 对应的主头文件叫 `foo_test.h` / `foo-test.h` 这类名字，
这样测试文件的主头文件也会被排到第一组。

#### 指针、空格、构造函数

| 选项 | 我们的值 | 为什么 |
| --- | --- | --- |
| `PointerAlignment` | `Left` | 写成 `int* p` 而不是 `int *p`。**这个争论在这份文件里终结了**，不用再讨论 |
| `SpacesInParentheses` | `false` | `f(x)` 不是 `f( x )` |
| `SpacesInConditionalStatement` | `false` | `if (x)` 不是 `if( x )`。注意 `if` 和 `(` 之间那个空格由别的选项控制，这一条管的是括号**里面** |
| `SpacesInAngles` | `false` | `vector<int>` 不是 `vector< int >` |
| `SpacesInCStyleCastParentheses` | `false` | `(float)x` 不是 `( float )x` |
| `SpaceInEmptyParentheses` | `false` | `f()` 不是 `f( )` |
| `BreakConstructorInitializers` | `AfterColon` | 构造函数的初始化列表，冒号后换行：`Foo()\n    : a_(1),\n      b_(2) {}` |
| `BreakConstructorInitializersBeforeComma` | `false` | 逗号跟在上一行末尾，而不是放到下一行开头 |
| `ConstructorInitializerAllOnOneLineOrOnePerLine` | `false` | 不强制"要么全在一行、要么一行一个"，允许按宽度自然折行 |
| `MacroBlockBegin` / `MacroBlockEnd` | `''`（空） | 没定义自定义的宏块。如果项目里有 `BEGIN_NAMESPACE` / `END_NAMESPACE` 这种宏，要在这里写上，否则宏里面的代码不会被缩进 |

### 你应该看到什么

这段视频的字幕基本就是上面这张表。**看完之后你应该能做到两件事**：

1. 随便指一条配置，说出它管的是什么
2. 说出 `AllowShortIfStatementsOnASingleLine: Never` 为什么和调试有关

### 如果没有

| 你的画面 | 原因 | 怎么办 |
| --- | --- | --- |
| 打开 `.clang-format` 没有语法高亮 | 文件是 YAML，CLion 默认认得 | 无所谓，纯文本也能看 |
| CLion 提示某个选项"未知" | CLion 自带的 clang-format 版本比你抄的配置旧/新 | 看 `03-3` 里换外部 clang-format 的办法；能跑通就不用管 |
| 想改某条配置试试效果 | —— | 直接在 `.clang-format` 里改，CLion 保存后会自动重新读（`03-3`） |

---

## 03-3 · 在 IDE 里用它：必须让 IDE 读工程配置

> 🎬 视频 03-3 · 00:00

**这一段是这一节最容易出错的地方。**

### 关键问题：IDE 可能用的是它自己的规则

CLion 和 VS Code 都**自带格式化功能**。如果你不告诉它"去读工程里的 `.clang-format`"，
它按自己的默认规则格式化——**结果就是：你按了格式化快捷键，
但代码不符合工程的 `.clang-format`，HW4 的自查会挂。**

而且这个错误很难自己发现：格式化确实执行了，代码确实变整齐了，
**只是不是工程要的那种整齐**。

### CLion 里怎么开（两个版本的路径都写上）

**新版本（2024.3 之后）**：

**Settings → Editor → Code Style → C/C++ → General → C/C++ formatting engine**，
选 **Clang-Format**。

或者选 **CLion formatter**，然后勾上下面的
**Read code style from .clang-format files**——
这样它用的是 CLion 的格式化引擎，但规则从 `.clang-format` 里读。

**老版本**：

**Settings → Editor → Code Style** 页面上有一个
**Enable ClangFormat** 复选框（有些版本叫 `Use clang-format`），勾上。

> 两种说法其实是同一个设置的演进。**你按自己版本上的实际字样找**——
> 如果你在 Code Style 页面上看到了 `Enable ClangFormat` 这行字，勾它就是；
> 如果看到的是一个下拉框写着 `C/C++ formatting engine`，就选 `Clang-Format`。

**还有一个更快的入口**：打开一个 `.cpp` 文件，
**状态栏**（窗口最下面那一条）上有一个格式切换器，点开就有 **Enable ClangFormat**。

### 怎么确认它真的在读工程配置

**状态栏切换器 → Show ClangFormat Options for Edited File**。

**你应该看到**：一个列表，显示 CLion 从 `.clang-format` 里读到的实际选项值。
**重点看两条**：

```text
IndentWidth = 4
AllowShortIfStatementsOnASingleLine = Never
```

如果这里显示 `IndentWidth = 2`，说明它用的不是工程配置（要么没开 ClangFormat，
要么 `.clang-format` 不在它以为的位置）。

同一个切换器里还有 **Open '.clang-format' for...**，直接跳到那份文件。

### 快捷键：以你自己 IDE 的实际配置为准

| IDE | 常见默认键位 |
| --- | --- |
| **CLion / IntelliJ 系列** | `Ctrl + Alt + L` |
| **VS Code** | `Shift + Alt + F` |
| 装了 Eclipse / VS 键位方案的人 | 可能是 `Alt + Shift + F` |
| 其它 | 在菜单里找 **Code → Reformat Code** |

> **不要背快捷键，找到那个功能就行。**
> 上面第 3 行不是凑数的：真的有人装过 VS 键位方案，
> 然后发现 `Shift+Alt+F` 和 `Ctrl+Alt+L` 都没反应，
> 以为 IDE 坏了。**在菜单里点一次，顺便看一眼它旁边写的快捷键是什么。**

**菜单路径**：**Code → Reformat Code**（对当前文件或选中范围）。

### 操作方式：先选中范围，再按

**在项目树里选中 `base` 这个目录**，再按格式化快捷键。

- 选中目录 → 格式化整个目录
- 选中文件 → 格式化这个文件
- 什么都不选、光标在编辑器里 → 格式化**当前文件**（不是整个工程，这点比很多人想的安全）

CLion 会弹一个确认框告诉你"将影响 N 个文件"，**看清楚 N 是多少**——
这一步就是 `03-4` 说的"控制爆炸半径"的手动版。

### 你应该看到什么

```text
① 格式化前后打开 base/math.h 对比：
     缩进从 2 空格变成 4 空格
     if (v < lo) return lo; 被拆成两行
② 左边栏（Project 面板）里被改动的文件变色，git 状态变成 modified
③ Alt+9 → Local Changes 里能看到的改动就是你刚才格式化的那些文件
```

**用 `git diff` 确认范围**（这一步不能省）：

```bash
cd EC-Training-Labs/day0/project
git status
git diff --stat
```

**你应该看到**：`git status` 里只有 `base/` 下面的文件是 modified。
如果 `app/`、`tests/`、`mcu/` 也冒出来了，说明范围开大了——见 `03-4` 的补救办法。

### 如果没有

| 你的画面 | 原因 | 怎么办 |
| --- | --- | --- |
| 按了快捷键没反应 | 键位被改过 | 菜单里找 **Code → Reformat Code**；或看自己的键位映射 |
| 格式化后缩进还是 2 空格 | **没开 ClangFormat**，用的是 IDE 自己的规则 | 回本节开头，确认 Settings 里的设置；再用 Show ClangFormat Options 验证 |
| 格式化后和同学的结果不一样 | 两边用的 clang-format 版本不同 | 看 **Settings → Editor → Code Style → C/C++ → General → Clang-Format**，可以勾 `Use external clang-format instead of the bundled one` 指定同一份。作业阶段不用纠结，能过自查就行 |
| 格式化把整个工程都改了 | 选中的是工程根目录 | `git restore app/ tests/ mcu/` 撤回，只留 `base/` |
| 改了 `.clang-format` 没生效 | 有的版本要重开文件 | 关掉文件重开；或者改完等一下，CLion 一般会自动重新读 |

---

## 03-4 · 格式化范围的纪律

> 🎬 视频 03-4 · 00:00

**这一段比前面所有配置加起来都重要。**

### 不要顺手把整个仓库格式化

你在 HW2、HW3 里只动过 `base/`（`math.h` 和新建的 `angle.cpp`）。
`app/`、`tests/`、`mcu/` 是别人写的，你连看都没看过。

**如果你手一滑格式化了整个仓库，会发生三件事：**

**① review 的人什么都看不出来。**
你只改了 20 行逻辑，diff 里却有 800 行缩进。看 diff 的人会在第 30 行放弃，
然后点 Approve——**你的 bug 就这样混进去了**。

**② `git blame` 废了。**
每一行都变成"上次是格式化那次改的"。想知道"这段归一化逻辑当初为什么这么写"，
blame 查到的是一个格式化的提交，真正的作者信息没了。
（在 CLion 里就是左边栏右键 → **Annotate with Git Blame**，你可以自己试一下
格式化前后同一行的归属变了没有。）

**③ 后面合并会打架——这一条最贵。**
你把整个仓库的文本重排了一遍。队友在他自己的分支上改了其中几个文件。
合并的时候，Git 看到的是"**你把这几百行都改了，他也把其中几行改了**"，
于是**冲突从 3 行变成 40 行**，而且这 40 行里你根本分不清哪一行是真冲突。

> **HW5 里你会亲手遇到这件事。** 到那时候回想一下这里：
> 冲突那一页会同时出现「你加的那一行」和「队友加的那一行」，
> 而如果之前格式化过整个仓库，那一页会变成整篇文件都是冲突标记——
> 你根本不知道哪一边该留。
>
> 这不是"不许格式化"，而是——
> **格式化和任何改动一样，要控制爆炸半径。**

### 只格式化你负责的目录 / 文件

HW4 的要求是**只格式化 `day0/project/base/` 这一个目录**。

判断标准很简单：

> **这一行代码，我能不能说清楚它为什么长这样？**
> 说不上来的目录，就不是你该动的。

真要统一全仓库的风格，那是**单独一件事、单独一次提交、单独一次讨论**——
而不是你顺手按一下快捷键。

### 格式化必须单独一个 commit

`style:` 前缀，不和任何逻辑改动混在一起：

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

`style` 这个前缀在 Git 课的类型表里是保留项（`feat` / `fix` / `refactor` / `docs` /
`test` / `chore` / `tune` 之外的补充），**看到 `style:` 就知道这个提交不该有行为改动**，
review 的时候可以直接跳过内容看范围。

**你应该看到什么**：

```bash
git show --stat HEAD
```

```text
commit 8f3c1a2...
Author: Zhang San <zhangsan@example.com>
Date:   ...

    style: apply clang-format to base/

 base/math.h | 42 +++++++++++++++++++++++++-------------------------
 base/angle.cpp | 18 +++++++++---------
 2 files changed, 30 insertions(+), 30 deletions(-)
```

**这个提交里只有 `base/` 下的文件**，而且每个文件的增删行数差不多
（格式化是"改一行 = 加一行删一行"，所以 `+` 和 `-` 接近）。
如果 `--stat` 里出现了 `app/` 或 `tests/`，说明范围开大了。

**为什么必须单独一个 commit**，三个具体理由：

| 理由 | 说明 |
| --- | --- |
| 真正的修复会被淹没 | "格式化 + 修 bug"混在一起，review 的人找不出那两行 |
| 想单独回退做不到 | 以后要退掉那个 bug 修复，会把格式化也一起退掉 |
| `blame` 指向错误的提交 | 同上，历史可读性直接没了 |

这就是 Git 课里 **atomic commit** 那句话：
**一个 commit 只表达一个逻辑变化。** "重新排版"是一个逻辑变化，"修 bug"是另一个。

### HW4 和 HW5 的咬合点

HW4 的这个坑不是老师编的，是设计好的：

```text
HW4：你跑 clang-format，把整个 base/ 格式化了一遍
      ↓
HW5：你会发现"这一坨格式化把 HW2 的 bug 修复淹没了"
      ↓
     你在 HW5 里必须把它们拆成不同的提交（Task 7）
```

**自己撞一次，比听十遍有用。** 到 HW5 Task 7 的时候你会需要按 hunk 挑着提交，
CLion 里的做法见 `02-5`。

### 已经搞混了怎么办

**情况 A · 范围开大了，格式化到了不该动的目录**

```bash
git status                    # 先看清有哪些文件被改了
git restore app/ tests/ mcu/  # 撤回这些目录（工作区的改动直接丢弃）
```

> `git restore <路径>` 会**丢弃**工作区里这些文件的改动，**不可恢复**。
> 所以敲之前先 `git status` 确认这些文件里没有你自己写的东西。

**情况 B · 格式化和逻辑改动混在一个 commit 里了**

```bash
git reset --soft HEAD~1       # 撤销这次提交，改动全部回到暂存区
git restore --staged .        # 全部退回工作区
git add base/math.h           # 先只提交逻辑改动
git commit -m "fix(motor): ..."
git add base/                 # 再单独提交格式化
git commit -m "style: apply clang-format to base/"
```

`--soft` 是关键：它只动提交记录，**不动你的代码**。

**情况 C · 格式化之后测试挂了**

说明你（或者某个工具的误操作）改到了逻辑。

```bash
git diff --ignore-all-space    # 忽略空白，看真实改动
```

**如果这条命令列出了文件，那些就是真实改动**，逐个看回去。
格式化不该改变程序行为——真改了，就不是格式化，是改代码。

### 如果没有

| 你的画面 | 原因 | 怎么办 |
| --- | --- | --- |
| 自查说"base/ 看起来没格式化过" | `base/` 里有文件漏了 | 选中整个 `base` **目录**再按，不要只选当前文件 |
| `git status` 里冒出 `app/` `tests/` 一堆改动 | 范围开成了整个项目 | `git restore app/ tests/ mcu/` |
| 格式化改动和别的改动混在一个 commit 了 | 提交前没分开 add | 上面的情况 B |
| `git diff --ignore-all-space` 还是显示有改动 | 见下面的说明 | 先确认是不是"一行拆成两行"这类结构性改动 |

> **关于 `--ignore-all-space` 的一个诚实说明**：
> 它忽略的是**空白**，不是"行的拆分"。
> 如果 `if (v < lo) return lo;` 被拆成了两行，
> 那么即使忽略空白，diff 里也会看到这几行——**那不是逻辑改动**。
>
> 所以 HW4 里说这条命令"几乎没有改动"，指的是**除缩进和这种拆行之外没有别的**。
> 判断标准是：你能逐条说出每一处改动是哪种排版规则造成的。

---

## 03-5 · 命令行：提一句就够

> 🎬 视频 03-5 · 00:00

**这一节不是主线。** 大部分人不装 `clang-format` 这个命令行工具，
因为 CLion 里自带一份，用的是同一个引擎、读的是同一份配置。

但你要知道有这两条命令，因为**自查工具用的就是它们**：

```bash
# 原地格式化（-i = in-place，直接改文件）
clang-format -i base/math.h

# 只检查，不改文件；有需要改动的地方就返回失败（非 0 退出码）
clang-format --dry-run -Werror base/math.h
```

`--dry-run -Werror` 正是 HW4 自查里的检查方式：
**它不修改任何东西，只是告诉你"这个文件不符合 `.clang-format`"**。

几个细节：

| 参数 | 说明 |
| --- | --- |
| `-style=file`（默认） | 从当前目录往上找 `.clang-format`。这就是"用工程配置"的意思 |
| `--style=LLVM` | 用内置的 LLVM 风格，**忽略工程配置**——不要用它来验证作业 |
| `-i` | 直接改文件。**改完记得跑测试** |
| `--dry-run` | 不写文件，只报告 |

**Windows 上要装它的话**：`winget install LLVM.LLVM`，
或者从 LLVM 的 release 页下 `LLVM-xx.x.x-win64.exe`，
装完 `clang-format.exe` 在 `C:\Program Files\LLVM\bin\`。
装完在 Git Bash 里 `clang-format --version` 应该有输出。
**不装完全不影响 HW4**。

### HW4 的完整流程（照着做）

```bash
cd EC-Training-Labs/day0/project

# ① 在 IDE 里只格式化 base/（03-3），然后看规模
git diff --stat
git diff --ignore-all-space --stat

# ② 确认没弄坏东西
python tools/build.py                  # 期望 encoder 4/4 · clamp 4/4

# ③ 单独提交
git add base/
git diff --staged --stat
git commit -m "style: apply clang-format to base/"

# ④ 推上去
git push
```

**自查**（在仓库根目录，也就是 `EC-Training-Labs/` 这一层）：

```bash
python tools/grade.py hw4 .
```

**你应该看到什么**（`grade.py` 的输出）：

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

**提交的截图**：`git diff --stat` 和 `git diff --ignore-all-space --stat` 两张。
这两张图同时说明两件事——**你确实格式化了，而且没改任何逻辑**。

### 如果没有（自查 FAIL 的三种典型）

| 自查的那一行 | 原因 | 怎么办 |
| --- | --- | --- |
| ❌ 代码符合 clang-format / "base/ 看起来没格式化过" | ① 没开 ClangFormat，用的还是 IDE 自己的规则；② 格式化时只选中了单个文件，`base/` 里有漏的 | 回 `03-3` 确认设置；在项目树里**选中 `base` 目录**再按格式化 |
| ❌ 有独立的格式化提交 | 格式化改动和逻辑改动混在一个 commit 里了 | `git reset --soft HEAD~1`，然后分两次 `add` + `commit`（见 `03-4` 的情况 B） |
| ❌ 测试全部通过（测试挂了） | 格式化不该改行为，挂了说明误改了逻辑 | `git diff --ignore-all-space` 看真实改动，改回去 |

> 自查明细里写什么就改什么，**改完重跑一遍 `grade.py`，不要直接交**。

---

## 一页速查

| 我想…… | 怎么做 |
| --- | --- |
| 让 IDE 读工程配置 | CLion：**Settings → Editor → Code Style → C/C++ → General** → `Clang-Format`（老版本：**Settings → Editor → Code Style → Enable ClangFormat**） |
| 确认它在读哪份配置 | 状态栏切换器 → **Show ClangFormat Options for Edited File**，看 `IndentWidth` 是不是 4 |
| 格式化 | CLion `Ctrl+Alt+L`（**以自己键位为准**）；VS Code `Shift+Alt+F`；菜单 **Code → Reformat Code** |
| 只格式化一个目录 | 在项目树里**选中目录**，再按格式化 |
| 看格式化动了多少 | `git diff --stat` |
| 看有没有真的改逻辑 | `git diff --ignore-all-space` |
| 单独提交格式化 | `git add base/` → `git commit -m "style: apply clang-format to base/"` |
| 撤回格式化范围开大的部分 | `git restore app/ tests/ mcu/` |
| 把混在一起的提交拆开 | `git reset --soft HEAD~1` 然后分两次 add + commit |
| 命令行检查 | `clang-format --dry-run -Werror <file>`（**不是主线，不装也行**） |

---

## 看完之后

去做 **HW4**。做完之后你手上是一个**测试全绿、提交历史清晰**的工程，
下一步（HW5）就是把这四份作业做的事情放进真实的团队协作流程里：
开分支、挑着提交、推上去、同步上游、解决一次真的冲突。

> **HW5 会检查你 HW1–HW4 的 commit message。**
> 如果你在 HW1–HW4 里写过 `update` 这种 message，回去把它改好
> （`git rebase -i` 改写，或者补一条说明性的新提交）。
