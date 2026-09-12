# 录播 02 · CLion 基本环境配置
<!-- ⚠️ 这个文件由 lab/sync_grader.py 从 Tools/02-clion-setup.md 复制而来。
     要改请改那份，然后重新同步 —— 不要直接改这里。 -->

> ℹ️ **这段录播还没发布。** 下面的 `🎬 视频 0X-Y · 00:00` 是分段占位符 ——
> 时间戳会在录像上线后回填。**在此之前，本文是自足的**：每一段都写了
> 「看什么、看到什么算过」，照着文字和截图走完是一样的。

| 项目 | 内容 |
| --- | --- |
| **这节讲什么** | 为什么用 CLion；工具链怎么配；CLion 是怎么"直接打开"一个 CMake 工程的；**CMake 生成器这个坑**；构建 / 运行 / 调试；Git 集成（`Alt+9` / `Ctrl+K` / 按 hunk 暂存）；中文乱码与构建目录清理 |
| **多长时间** | 约 30 min，分 6 段（`02-1` ~ `02-6`），每段 3–6 min |
| **对应哪份作业** | **HW1（把项目跑起来）、HW2（修编码器回绕）——`02-1` ~ `02-4` 是前置**；HW5 的 Git 操作在 `02-5`；HW4 的 Reformat Code 见讲义 `03-clang-format.md` |

> **这一段是"键盘可见"要求最强的录播。** CLion 的所有常用操作都有快捷键，
> 而按快捷键和点菜单在画面上长得一模一样。如果录的时候没叠按键显示，
> 学生会以为你是点某个按钮做到的，然后找不到那个按钮。
> 录制要求见 `README.md` §2.3。

**分段表**（录的时候按这个切）：

| 段 | 标题 | 目标时长 |
| --- | --- | --- |
| 02-1 | 为什么用 CLion，以及它是怎么打开工程的 | 4 min |
| 02-2 | 工具链配置 | 5 min |
| 02-3 | CMake 生成器这个坑 | 6 min |
| 02-4 | 构建 / 运行 / 调试 | 6 min |
| 02-5 | Git 集成 | 6 min |
| 02-6 | 收尾：中文乱码、构建目录、清缓存 | 3 min |

---

## 02-1 · 为什么用 CLion，以及它是怎么打开工程的

> 🎬 视频 02-1 · 00:00

### 先说清楚：不是"用 CLion 替代 Keil"

| | Keil µVision | CLion |
| --- | --- | --- |
| 代码补全 | 基本靠模板 | 语义级补全，能补类成员、参数名 |
| 跳转 / 找引用 | 有限 | `Ctrl+B` 跳定义，`Ctrl+Alt+B` 找实现，`Ctrl+Shift+F` 全仓库搜 |
| 重构 | 基本没有 | Rename / Extract Function / Change Signature，改一处全工程跟着变 |
| 构建系统 | 私有的 `.uvprojx` | **标准 CMake**，跨平台、能进 CI |
| Git 集成 | 没有 | 内置（`02-5`） |
| 格式化 | 没有 | clang-format，读工程里的 `.clang-format`（讲义 `03`） |
| **调试嵌入式** | **强**：外设寄存器视图、SWO、Flash 编程算法都是原生的 | 弱：要额外配 OpenOCD，没有外设寄存器视图 |
| **烧录** | 原生支持 ST-Link / ULINK / J-Link | 要 OpenOCD 或插件 |
| 平台 | 只有 Windows | Windows / macOS / Linux |

**结论**：**写代码用 CLion，烧录调试用 Keil。** 真实仓库里两边都留着——
你去看 `mcu/stm32f407/` 下面，`CMakeLists.txt` 和 `MDK-ARM/*.uvprojx` 是并存的。

所以这一节讲的不是"换个 IDE"，是"**给你加一个写代码更快的工具**"。
Keil 那一套（讲义 `01`）一样要会。

### CLion 不需要"建工程"

这是从 Keil 转过来的人第一个不习惯的地方：

> **CLion 没有"新建工程"这一步（对已有 CMake 工程来说）。**
> **它直接读 `CMakeLists.txt`。**

对比一下：

| | Keil | CLion |
| --- | --- | --- |
| 工程文件是什么 | `.uvprojx`（XML，私有格式） | `CMakeLists.txt`（就是构建脚本本身） |
| 加一个源文件 | 在 IDE 里加进 Group，`.uvprojx` 变一次 | 改 `CMakeLists.txt`，加一行文件名 |
| 工程文件要不要提交 | 要（`01-7`） | 要（它本来就是个正经源文件） |
| IDE 自己的配置 | `.uvoptx` / `.uvguix.*`（不该提交） | `.idea/`（**已经在 `.gitignore` 里**） |

**一个 `.uvprojx` 只能被 Keil 打开；一个 `CMakeLists.txt` 能被 CLion、VS Code、命令行、CI 用。**

### 打开作业工程

仓库里**有两个 CMake 工程**，看你做哪条线：

| 线 | 打开哪个目录 | 做什么 |
| --- | --- | --- |
| Git 线（`HW1`–`HW5`） | `EC-Training-Labs/day0/project` | 构建 → 修 bug → 链接错误 → 格式化 → Git 提交 |
| C++ 线（`cpp1`–`cpp4`） | `EC-Training-Labs/day0/cpp` | 声明与定义 → 函数 → 枚举与指针 → 位运算 |

**File → Open** → 选中上表里对应的**那个目录** → OK。

> ⚠️ **一定选目录，不要选文件。** 选了一个 `.cpp` 的话，
> CLion 不知道该把哪个目录当工程根，结果就是"满屏红、头文件全找不到"。
> 这是新人第一天最常见的求助，没有之一。
>
> **两个工程是两个窗口。** 同时做两条线的话，CLion 里开两个窗口，
> 别在一个窗口里 Open 第二个 —— 想切工程时先 **File → Close Project**。

CLion 会自动做这几件事：找到 `CMakeLists.txt` → 配 CMake → 建一个构建目录
→ 跑一次 configure → 建索引。右下角会有进度条。

### 看一眼这个 `CMakeLists.txt`

```cmake
cmake_minimum_required(VERSION 3.16)
project(day0_git_lab CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE Debug)
endif()

add_library(day0_core
  app/control.cpp
  app/motor_monitor.cpp
  app/clamp.cpp
)
target_include_directories(day0_core PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})

enable_testing()
add_subdirectory(tests)
```

**逐行说**：

| 行 | 意思 |
| --- | --- |
| `cmake_minimum_required(VERSION 3.16)` | 低于这个版本的 CMake 直接报错退出，避免"版本不同行为不同" |
| `project(day0_git_lab CXX)` | 工程名 + 只用 C++（不启用 C 和 Fortran，configure 更快） |
| `set(CMAKE_CXX_STANDARD 17)` | 用 C++17 |
| `if(NOT CMAKE_BUILD_TYPE) ... Debug` | **没指定就默认 Debug**。Debug 带调试信息、不开优化——`02-4` 里断点能不能打准全靠它 |
| `add_library(day0_core ...)` | **这一行是 HW3 的主战场**：新建 `base/angle.cpp` 之后要加在这里，不加就 `undefined reference` |
| `target_include_directories(... PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})` | 把工程根目录加进头文件搜索路径。**这就是为什么代码里能写 `#include "app/control.h"` 这种从工程根算起的路径** |
| `enable_testing()` + `add_subdirectory(tests)` | 启用 CTest，然后把 `tests/` 目录也加进来 |

`tests/CMakeLists.txt` 是配套的另一半：

```cmake
add_executable(test_encoder test_encoder.cpp)
target_link_libraries(test_encoder PRIVATE day0_core)
add_test(NAME encoder COMMAND test_encoder)

add_executable(test_clamp test_clamp.cpp)
target_link_libraries(test_clamp PRIVATE day0_core)
add_test(NAME clamp COMMAND test_clamp)
```

`add_executable` 建可执行文件，`target_link_libraries` 把它和 `day0_core` 连起来，
`add_test` 把它注册成一个 CTest 用例。**CLion 就是靠 `add_test` 知道有哪些测试可以跑的。**

### 你应该看到什么

```text
① 底部出现 CMake 工具窗口，内容大致是：
     -- The CXX compiler identification is GNU 14.2.0
     -- Detecting CXX compiler ABI info - done
     -- Configuring done
     -- Generating done
     -- Build files have been written to: .../day0/project/cmake-build-debug
   没有红字。

② 右上角运行配置下拉框里能选到 test_encoder / test_clamp。

③ 左侧 Project 面板里是一棵正常展开的树：
     project
     ├── app/  base/  tests/  tools/  mcu/
     ├── CMakeLists.txt
     └── .clang-format

④ 打开 app/motor_monitor.cpp，#include "base/math.h" 那行不是红的。
```

**一个快速的正确性检查**：在 `app/arm.h` 里按住 `Ctrl` 点一下 `ClampState`，
应该能跳到 `enum class ClampState` 那一行。跳不过去说明索引或头文件路径有问题。

### 如果没有

| 你的画面 | 原因 | 怎么办 |
| --- | --- | --- |
| 满屏红波浪线，头文件全找不到 | **打开的是单个文件，不是目录** | File → Open 重新选 `day0/project` 目录 |
| CMake 面板一片红 | CMake 配置失败 | 看 `02-3`，八成是生成器或工具链 |
| 运行配置下拉框里只有 `Current File` | CMake 没配置成功，CLion 不知道有哪些目标 | 先让 CMake 面板变绿 |
| 右下角一直在"Indexing" | 正常，第一次要建索引 | 等它跑完；超过 10 分钟去 `02-6` 看清缓存的办法 |
| 提示 "This file does not belong to any project target" | 这个文件没被任何 `add_*` 引用 | 是预期行为：`base/angle.cpp` 在 HW3 加进 `CMakeLists.txt` 之前不属于任何目标 |

---

## 02-2 · 工具链配置

> 🎬 视频 02-2 · 00:00

**做什么**：**Settings → Build, Execution, Deployment → Toolchains**，
把 CMake、编译器、调试器的路径填对。

### 这一个页面上的每个字段

| 字段 | 填什么 | 填错的后果 |
| --- | --- | --- |
| **Name** | 一个名字（`MinGW` / `Visual Studio` / `WSL`） | 只是标签，随便起 |
| **CMake** | CLion 自带的就行（`Bundled CMake 3.30.x`） | 用系统装的也行，但**别指向一个不存在的路径** |
| **Build Tool** | Ninja（CLion 自带一份）或 `mingw32-make` | 这一栏和 `02-3` 的生成器是配套的，两个都要对 |
| **C Compiler** | `gcc.exe` 的完整路径，或 `cl.exe` | **空着就报 `No CMAKE_C_COMPILER could be found`** |
| **C++ Compiler** | `g++.exe` 的完整路径，或 `cl.exe` | **空着就报 `No CMAKE_CXX_COMPILER could be found`** |
| **Debugger** | `gdb.exe`（MinGW）或 CLion 自带的 LLDB | 空着能编译能运行，但**调试按钮是灰的** |
| **Toolset** | 一般空着 | —— |

**这一栏填错的话，CLion 会一直说找不到编译器，而且报错信息完全不指向真正的原因。**
最典型的是：编译器路径是空的，CMake 报的是 `CMAKE_CXX_COMPILER not set, after EnableLanguage`——
你盯着这一行看不出该去 Toolchains 页面填东西。

### 工具链从哪来（Windows 上三条路）

| 方案 | 怎么来 | 优点 | 缺点 |
| --- | --- | --- | --- |
| **CLion 自带的 MinGW**（推荐给新人） | 装 CLion 时勾上，或在 Settings → Toolchains 里点 `+` → `MinGW` → 让它自动检测 | 零配置；不污染系统 PATH | 版本偏老；只在 CLion 里能用 |
| **MSYS2 的 MinGW-w64** | 装 MSYS2，`pacman -S mingw-w64-ucrt-x86_64-gcc`，把 `C:\msys64\ucrt64\bin` 填进去 | 版本新；命令行也能用 | 多装一个东西 |
| **Visual Studio（MSVC）** | 装 VS 时勾"使用 C++ 的桌面开发" | 和 VS 生态一致 | 命令行和 CMake 生成器的行为跟 MinGW 不一样；同学之间对不上 |

**Day 0 的建议**：**用 CLion 自带的那套**。作业只需要 `g++` + CMake + CTest，
自带工具链完全够。想用命令行 `python tools/build.py` 的时候，
如果 PATH 上没有 `g++`，`build.py` 会打印一行提示然后交给 CMake 自己找——
它**不会**因为这个失败。

### 怎么确认 CLion 真的认到了

**三个地方，全绿才算认到**：

**你应该看到什么**：

```text
① Settings → Build → Toolchains
   每一行后面有绿色的 Detected 标记
   CMake / Build Tool / C Compiler / C++ Compiler / Debugger 五栏都有路径

② 底部 CMake 工具窗口，重新配置之后能看到：
     -- The CXX compiler identification is GNU 14.2.0
     -- Check for working CXX compiler: C:/.../g++.exe - skipped
     -- Detecting CXX compile features - done
     -- Configuring done
   编译器识别出来了，而且路径是你期望的那一个。

③ 顶部工具栏的 Build 按钮（🔨）能点，点完有编译输出。
```

**点一下 CMake 面板左上角的 🔄（Reload CMake Project）就会重新走一遍配置**，
改完工具链之后一定要点它，否则改的东西不生效。

### 多个工具链 / 多个 profile

CLion 允许你同时留好几套工具链，然后建多个 **CMake profile**，
每个 profile 绑一套工具链 + 一个构建类型 + 一个构建目录：

```text
Settings → Build → CMake
  ┌ Profile: Debug   → Toolchain: MinGW   → Build type: Debug   → Build dir: cmake-build-debug
  └ Profile: Release → Toolchain: MinGW   → Build type: Release → Build dir: cmake-build-release
```

**作业只要一个 Debug profile。** 但你要知道有这么个东西——
`02-6` 里"构建目录乱了怎么清"就是在这一页操作的。

### 嵌入式工具链（`arm-none-eabi`）要不要配

**Day 0 的作业链（HW1–HW5）全是 PC 上的 g++ 工程，不需要它。**

如果你要在 CLion 里编 STM32 固件（真实战队仓库的用法），那需要：

- `arm-none-eabi-gcc` 工具链 + 一个 **CMake toolchain file**（指定 `CMAKE_C_COMPILER` 等）
- OpenOCD 作为"调试器"（CLion 里配成 GDB Server）
- 真实仓库里对应的东西是 `mcu/stm32f407/CMakeLists.txt` 和 `.config/openocd.cfg`

**这一段不录**，等你真要做板子上的东西时再单独学。现在知道"CLion 也能编 STM32"就够了。

### 如果没有

| 你的画面 | 原因 | 怎么办 |
| --- | --- | --- |
| Toolchains 页面某一行是红色 | 路径指向的文件不存在 | 点右边文件夹图标重新选；或者删掉这一行让 CLion 重新检测 |
| `No CMAKE_CXX_COMPILER could be found` | C++ Compiler 那栏空着 | 填上 `g++.exe` 的完整路径 |
| 调试按钮是灰的 | Debugger 那栏空着 | 选 CLion 自带的 LLDB，或填 MinGW 的 `gdb.exe` |
| 识别出的编译器不是你想用的那个 | 系统 PATH 上有另一个 g++ | 在 Toolchains 里显式指定完整路径，别用自动检测 |
| 装了 32 位的 MinGW | 链接报 `skipping incompatible ... while searching for -lstdc++` | 重新装 64 位（`x86_64`，不是 `i686`） |

---

## 02-3 · CMake 生成器这个坑

> 🎬 视频 02-3 · 00:00

**这一段单独录，因为它是 Day 0 现场翻车最多的地方。**

### 现象

配置 CMake 的时候，底部 CMake 面板报错，长这样：

```text
CMake Error: Generator: execution of make failed. Make command was: nmake /nologo
```

或者：

```text
-- Building for: NMake Makefiles
CMake Error at CMakeLists.txt:2 (project):
  No CMAKE_CXX_COMPILER could be found.

  Tell CMake where to find the compiler by setting either the environment
  variable "CXX" or the CMake cache entry CMAKE_CXX_COMPILER to the full path
  to the compiler, or to the compiler name if it is in the PATH.
```

或者配置过了，但一点构建就报：

```text
'nmake' 不是内部或外部命令，也不是可运行的程序或批处理文件。
```

### 原因

**CMake 在 Windows 上的默认生成器是 `NMake Makefiles`。**

而 `nmake` 这个东西**只存在于 Visual Studio 的"开发者命令提示符"里**——
它不是系统自带的命令，也不是装 VS 就会进 PATH 的。
普通终端（还有 CLion）里没有 `nmake`，于是：

```text
生成器选了 NMake → 找不到 nmake → 没法用 MSVC 探测编译器
                 → CMake 报 "找不到 C++ 编译器"
```

**注意最后那句报错——它完全不指向真正的原因。**
真正的原因是"生成器选错了"，报出来的却是"找不到编译器"，
于是新人开始反复重装 MinGW，方向从一开始就错了。

### 怎么改（CLion 里）

**Settings → Build, Execution, Deployment → CMake** → 选中你的 profile →

**把 `Generator` 下拉框从默认值改成 `Ninja`。**

改完点 **Tools → CMake → Reset Cache and Reload Project**（或者 CMake 面板上的 🔄）。

其他可选项：

| Generator 选什么 | 前提 | 说明 |
| --- | --- | --- |
| **`Ninja`**（推荐） | `ninja.exe` 在 PATH 上，或填 CLion 自带的那个 | 增量构建最快，跨平台，错误输出干净 |
| `MinGW Makefiles` | PATH 上有 `mingw32-make` | 用 MinGW 自带的 make，慢一点但不需要额外装东西 |
| `Let CMake decide` | —— | 交给 CMake 猜。**在 Windows 上它会猜 NMake**，所以别选这个 |
| `Visual Studio 17 2022` | 装了 VS 且勾了 C++ 桌面开发 | 用 MSVC 编译，和 MinGW 的报错风格不一样 |

### 命令行上对应的命令

```bash
cd EC-Training-Labs/day0/project

# 推荐：显式指定 Ninja
cmake -S . -B build -G Ninja -DCMAKE_BUILD_TYPE=Debug
cmake --build build

# 或者用 MinGW 的 make
cmake -S . -B build -G "MinGW Makefiles" -DCMAKE_BUILD_TYPE=Debug
```

**你应该看到**：

```text
-- The CXX compiler identification is GNU 14.2.0
-- Detecting CXX compiler ABI info
-- Detecting CXX compiler ABI info - done
-- Check for working CXX compiler: C:/msys64/ucrt64/bin/g++.exe - skipped
-- Detecting CXX compile features
-- Detecting CXX compile features - done
-- Configuring done
-- Generating done
-- Build files have been written to: .../day0/project/build
```

**`-G` 只在空目录上生效。** 如果 `build/` 里已经有 `CMakeCache.txt`，换生成器会报：

```text
CMake Error: generator : Ninja
does not match the generator used previously: NMake Makefiles
Either remove the CMakeCache.txt file and CMakeFiles directory or choose a different binary directory.
```

**它已经把怎么办写在报错里了**——删掉重来：

```bash
rm -rf build
```

CLion 里对应的是 **Tools → CMake → Reset Cache and Reload Project**。

### 作业仓库已经替你处理了一半

`day0/project/tools/build.py` 里有这么一段逻辑（注释是原文）：

```python
def guess_generators() -> list[str]:
    """按可用性排出一串候选生成器。

    **为什么需要这个**：Windows 上如果没装 Visual Studio，cmake 会默认挑
    "NMake Makefiles" —— 而 nmake 只在 VS 的开发者命令提示符里才有，
    普通终端里会报 `nmake: no such file or directory`，看起来像 cmake 坏了，
    其实只是选错了生成器。
    """
```

它先按默认生成器试一次，**失败了再从"本机真的有"的生成器里挑一个重试**，
并且会打印：

```text
默认生成器不可用，改用 -G "Ninja" 重试 ……
$ cmake -S . -B build -DCMAKE_BUILD_TYPE=Debug -G Ninja
```

**所以 `python tools/build.py` 是能跑通的。**
但是——**CLion 的 CMake 配置是 CLion 自己发起的，不走 `build.py`**，
所以这个坑在 CLion 里照样会遇到，`02-3` 这一段不能跳。

### 如果没有

| 你的画面 | 原因 | 怎么办 |
| --- | --- | --- |
| 改了 Generator 但还是老报错 | 没重置 cache | Tools → CMake → Reset Cache and Reload Project |
| 报 `Could not create named generator Ninja` | 选了 Ninja 但 PATH 上没 `ninja.exe` | CLion 里把 Generator 下面的 Ninja 路径指向自带的那份；或者改用 `MinGW Makefiles` |
| 报 `CMAKE_MAKE_PROGRAM is not set` | Build Tool 那栏空着 | Settings → Build → Toolchains → Build Tool 填 `ninja.exe` 或 `mingw32-make.exe` |
| 命令行能编过，CLion 报错 | 两边用了不同的生成器/构建目录 | 看 CMake 面板第一行的 `Build directory`；CLion 默认用 `cmake-build-debug/`，`build.py` 用 `build/`，两个目录互不干扰，**这是正常的** |
| 想彻底重来 | —— | 删 `cmake-build-debug/` 和 `.idea/`，重开工程。**删之前先关掉 CLion**，不然文件被占用删不掉 |

---

## 02-4 · 构建 / 运行 / 调试

> 🎬 视频 02-4 · 00:00

**做什么**：把 `test_encoder` 跑起来，看到 HW1 期望的"3/4 passed"；
然后打断点、看变量、看调用栈。

### 工具栏上这几个按钮

| 按钮 | 快捷键 | 做什么 |
| --- | --- | --- |
| 🔨 Build | `Ctrl+F9` | 只构建，不运行 |
| ▶ Run | `Shift+F10` | 构建 + 运行 |
| 🐞 Debug | `Shift+F9` | 构建 + 进调试 |
| 运行配置下拉框 | —— | 选跑哪个目标：`test_encoder` / `test_clamp` / `All CTest` / `All targets` |

**`All CTest` 是 CLion 识别 `add_test` 之后生成的一个配置**，
它会按 CTest 的方式把两个测试都跑一遍——**和 `python tools/build.py` 里的 ctest 是同一件事**。

### 跑起来（HW1 的验证点）

选 `All CTest` → 点 ▶（`Shift+F10`）。

**你应该看到**（真实输出，`tools/build.py` 跑出来的也是这个）：

```text
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

> ### ⚠️ 现在这个失败是**对的**
>
> `test_encoder` 挂一个用例**不是你环境装坏了**，是工程里本来就有一个 bug。
> **HW1 不要动任何代码**，HW2 会带你修它。

### 调试：断点、变量、调用栈

在 `tests/test_encoder.cpp` 第 31 行（`forward across zero` 那一行）左边的灰色区域点一下，
出现红点。然后选 `test_encoder` 配置 → 点 🐞（`Shift+F9`）。

**你应该看到**：

```text
① 程序停在 tests/test_encoder.cpp:31，那一行整行高亮
② 底部 Debug 工具窗口自动打开，里面有几栏：
     Frames     ← 调用栈
     Variables  ← 当前作用域的变量
     Watches    ← 你手动加的表达式
     Threads
③ Variables 里能看到 fwd_wrap = {355.0, 359.0, 3.0, 7.0}
```

**单步 / 继续的快捷键**（这几个和 Keil 不一样，见下面的提醒）：

| 操作 | CLion | Keil |
| --- | --- | --- |
| 步过 Step Over | **`F8`** | `F10` |
| 步入 Step Into | **`F7`** | `F11` |
| 步出 Step Out | `Shift+F8` | `Ctrl+F11` |
| 继续 Resume | `F9` | `F5` |
| 打断点 | `Ctrl+F8` | 点左边框 |
| 运行到光标 | `Alt+F9` | —— |
| 求值 / 看表达式 | **`Alt+F8`** | Watch 窗口 |

> ⚠️ **同时用 Keil 和 CLion 的人会被这个搞晕**：两个 IDE 的快捷键体系完全不同。
> 最坑的一对是 **`F8`**：在 Keil 里它是"下载到 Flash"，在 CLion 里它是"步过"。
> 从 Keil 切过来的人按 `F8` 想下载，结果程序往前走了一行；
> 反过来在 CLion 里按 `F10` 想步过，什么都不会发生。
> **录这一段的时候要慢，把按键叠上去**——这是"键盘可见"最值得的几个操作之一。

**`Alt+F8`（Evaluate Expression）是新人最该学会的一个键**：
不用改代码、不用重新编译，就能算 `deg_normalize_180(-356.0f)` 是多少。
HW2 里"把两个数代进去算一遍"就可以直接用它。

**条件断点**：右键红点 → 填 `Condition`。调一个 1kHz 的循环时，
普通断点会停一万次，条件断点才能停在你关心那一帧。

**为什么断点会打不准**：因为优化。
确认 `02-2` 里 profile 的 **Build type 是 `Debug`**——
Debug 会带 `-g -O0`，Release 是 `-O2` 且可能把变量优化没。
`Variables` 里显示 `<optimized out>` 就是优化开着的典型症状。

### 让测试的输出看得见

`test_encoder` 的 `printf` 是直接写 stdout 的，CLion 跑 `All CTest` 的时候
不一定显示每个用例的明细。**要看明细就直接跑 `test_encoder` 这一个配置**
（下拉框里选 `test_encoder`），输出会完整打在 Run 窗口里。

命令行对照：

```bash
cd EC-Training-Labs/day0/project
python tools/build.py                    # 配置 + 构建 + ctest
python tools/build.py --no-test          # 只构建
python tools/build.py --clean            # 先删 build/ 再来
```

**`python tools/build.py` 跑完即使有测试失败，退出码也是 0**——
脚本里写明了："构建成功就算成功"，因为 HW1 阶段 `test_encoder` 本来就该挂一个用例，
不能让 ctest 的失败码把学生吓一跳。

### 如果没有

| 你的画面 | 原因 | 怎么办 |
| --- | --- | --- |
| 运行配置下拉框里没有 `test_encoder` | CMake 没配置成功 | 回 `02-3` |
| 点 Run 报 `Error running 'test_encoder': Cannot find ...` | 构建目录被删了/换了 | 重新构建一次；Tools → CMake → Reset Cache and Reload Project |
| 断点是灰的 / 点不动 | 没进调试模式，或者这一行不可执行（注释、空行） | 用 🐞 进调试；换个可执行的行 |
| 程序停在一个我没打断点的地方 | 崩了（收到信号） | 看 Call Stack 最上面一帧；HW2 是逻辑 bug，一般不崩 |
| 变量显示 `<optimized out>` | Build type 是 Release | Settings → Build → CMake → Build type 改 `Debug` |
| 测试全绿了 | **不可能**，除非你改了代码 | 你确定没动过 `base/math.h`？ |

---

## 02-5 · Git 集成

> 🎬 视频 02-5 · 00:00

**这一段的操作和线下 Git 课件、HW5 是同一件事的两种做法。**
命令行是底，IDE 是效率工具——**两个都要会**。

### `Alt+9` 打开 Git 工具窗口

窗口里有几个标签页：

| 标签 | 里面是什么 | 命令行对照 |
| --- | --- | --- |
| **Local Changes** | 工作区 + 暂存区的所有改动 | `git status` + `git diff` |
| **Log** | 提交历史、分支图 | `git log --oneline --graph` |
| **Console** | CLion 实际执行的 Git 命令 | —— |
| **Shelf** | 搁置（CLion 自己的功能，不是 Git 的） | `git stash` 的替代品 |

> 💡 **Console 标签值得单独看一眼。** 你在界面上点的每一步，
> 它都把对应的 Git 命令打出来了。**这是学 Git 命令最好的方式**——
> 先去点，再回来看它执行了什么。

### `Ctrl+K` 提交

按 `Ctrl+K` 弹出 **Commit** 窗口，里面是刚才 Local Changes 里的东西，
每个文件前面有勾选框。

**两个必须知道的细节**：

**① 灰色的文件是"未跟踪"（untracked）。**
`.gitignore` 没挡住的**新文件**不会自动进提交列表。
右键 → **Add to VCS**（`Ctrl+Alt+A`）之后它才会变绿，才能提交。

**② 可以按 hunk 勾选——这就是 atomic commit 的图形版。**

点文件名左边的三角展开，会看到这个文件里的每一块改动（hunk），
每块前面有自己的勾选框。**只勾你要提交的那一块，剩下的留在工作区。**

这就是命令行里的 `git add -p`：

```text
Commit 窗口里：展开文件 → 勾选第 2 个 hunk → 提交
命令行里：    git add -p → 对每块选 y/n → git commit
```

**这一条直接对应 HW5 Task 7**：三个 TODO 要拆成四个提交，
除了按文件拆（它们本来就在三个文件里），
**如果某次改动同时包含了格式化和逻辑修改，就要靠 hunk 级别来拆**。
排版和逻辑在同一个文件里混着的时候，只有 hunk 级别能救你。

> ⚠️ **Commit 窗口右侧有一个 `Reformat code` 勾选框，默认不勾。
> 不要勾它。**
> 它会在提交前把你改过的文件整个重新格式化一遍，
> 于是你的 commit 里混进了大量**你没打算改的格式改动**。
> 讲义 `03-clang-format.md` 的 `03-4` 讲的就是这件事的代价。

**你应该看到什么**：

```text
① Alt+9 打开后，窗口里有 Local Changes / Log / Console / Shelf 几个标签
② 改一行代码，Local Changes 里立刻出现这个文件；
   新文件是灰色的，右键 Add to VCS 之后变绿
③ Ctrl+K 弹出的 Commit 窗口里，每个文件前面有勾选框；
   展开文件能看到 hunk 级的勾选框
④ Ctrl+Shift+K 推送成功后，状态栏右下角提示 Push successful
```

### diff 视图怎么看

| 操作 | 快捷键 / 路径 | 说明 |
| --- | --- | --- |
| 看某个文件的 diff | Local Changes 里双击文件 | 打开对比窗口 |
| 从编辑器看当前文件 diff | `Ctrl+D` | 不用离开代码 |
| 切换左右对照 / 统一视图 | diff 窗口右上角的图标 | **小改动用统一视图更快看懂**；大改动用左右对照 |
| 忽略空白差异 | diff 窗口里的设置图标 → `Ignore whitespace` | 对应 `git diff --ignore-all-space`，**HW4 的验证就靠它** |
| 看某一行是谁写的 | 编辑器左边栏右键 → **Annotate with Git Blame** | 对应 `git blame`。HW4 里说"格式化会让 blame 失效"，就是看这个 |

### 分支、推送、更新

| 操作 | 路径 | 命令行 |
| --- | --- | --- |
| 新建 / 切换分支 | 右下角状态栏的分支名 → New Branch / 选一个 | `git switch -c fix/pickup-todos` |
| 推送 | `Ctrl+Shift+K` | `git push` |
| 更新（拉取） | `Ctrl+T` | `git pull` |
| 合并 | Log 里右键某个分支 → Merge into Current | `git merge upstream/drop-mode` |
| 看分支图 | `Alt+9` → Log | `git log --oneline --graph` |

**HW5 Task 9 的冲突**：合并的时候如果冲突，CLion 会弹一个 **Merge** 对话框，
点 `Merge` 打开三栏合并工具（左边你的、右边他们的、中间结果）。
**但 Day 0 我们要求你用命令行做这一次合并**——
原因在 HW5 里写了：冲突不是"选一边"，是要想清楚两边各自要什么，
第一次必须自己盯着冲突标记看一遍。IDE 的按钮会让你跳过这个理解过程。
**第二次开始随便你用哪个。**

### 和 HW5 的对照表

| HW5 的任务 | 命令行 | CLion 里 |
| --- | --- | --- |
| Task 1 看状态 | `git status` / `git log --oneline --graph -8` | `Alt+9` → Local Changes / Log |
| Task 2 开分支 | `git switch -c fix/pickup-todos` | 右下角分支名 → New Branch |
| Task 5 看改了什么 | `git diff` | `Ctrl+D` |
| Task 6 改 `.gitignore` | 直接编辑文件 | 一样，编辑文件 |
| Task 7 拆成四个提交 | `git add <file>` ×4 + `git commit` | Commit 窗口里逐个文件勾选 + 提交 |
| Task 8 推送 | `git push -u origin fix/pickup-todos` | `Ctrl+Shift+K` |
| Task 9 合并上游 | `git fetch` + `git merge` | Log 里右键 → Merge（**第一次建议用命令行**） |
| Task 10 解决冲突 | 编辑文件删冲突标记 | 三栏 Merge 工具 |
| Task 11 收尾 | `git push` / `git status` | `Ctrl+Shift+K` |

### 如果没有

| 你的画面 | 原因 | 怎么办 |
| --- | --- | --- |
| `Alt+9` 弹出来的东西是空的 | 这个目录不是 Git 仓库 | 确认你在 `EC-Training-Labs/` 下面；或者 **VCS → Enable Version Control Integration** |
| Commit 窗口里看不到某个新文件 | 它是 untracked，而且显示成了灰色 | 右键 → Add to VCS |
| 修改过的文件在 Local Changes 里显示成两个条目 | CLion 把"已暂存"和"未暂存"分开显示了 | 正常，这正是 Git 的暂存区模型，对应 Git 课件 Loop 2 |
| Push 报 `Permission denied (publickey)` | SSH key 没配好 | 见 `README.md` §3.1 和 §4 的第 ② 条 |
| Push 报 `rejected` / `fetch first` | 远端有你本地没有的提交 | 先 `Ctrl+T` 拉一次再推。**不要用 force push** |

---

## 02-6 · 收尾：中文乱码、构建目录、清缓存

> 🎬 视频 02-6 · 00:00

**做什么**：把三个最常来问的问题一次性讲掉。

### ① 中文乱码

三种情况，原因不一样：

**情况 A · 源文件里的中文注释在 CLion 里显示成乱码**

**Settings → Editor → File Encodings**：

```text
Global Encoding:        UTF-8
Project Encoding:       UTF-8
Default encoding for properties files: UTF-8
```

然后对已经乱码的文件：编辑器右下角点编码 → `Reload in UTF-8`。

**情况 B · 编译出来的程序，在 cmd 里打印中文是乱码**

源码是 UTF-8，但 Windows 控制台默认代码页是 GBK（936）。
最快的办法是让控制台切到 UTF-8：

```bash
chcp 65001
```

**你应该看到**：

```text
Active code page: 65001
```

**在 CLion 的 Run 窗口里通常不会乱**——CLion 内部按 UTF-8 处理。
所以"CLion 里正常、cmd 里乱码"是预期现象，不是你的代码有问题。
如果要每开一个终端都自动生效，在 Git Bash 的 `~/.bashrc` 里加一行 `chcp.com 65001 > /dev/null`，
或者干脆用 Windows Terminal 并把它默认的 profile 代码页设成 UTF-8。

**这一段的三件事都做完之后，你应该看到**：源文件里的中文注释正常显示、
`chcp` 之后控制台能正常打印中文、构建目录可以干净地删掉重建。

**情况 C · 编译时就报错或者中文变问号**

MinGW 的 g++ 默认按 UTF-8 读源码，一般没事。
用 MSVC 的话要显式告诉它源码是 UTF-8：在 `CMakeLists.txt` 里加

```cmake
add_compile_options(/utf-8)     # 只对 MSVC 有效
```

或者

```cmake
if(MSVC)
  add_compile_options(/utf-8)
endif()
```

**Day 0 的作业用 MinGW，不需要加这个。**

### ② 构建目录乱了 / 想清干净重来

CLion 的构建目录默认是 `cmake-build-debug/`，`build.py` 用的是 `build/`。
**两个目录互不干扰，这不是问题**，但你要知道哪个是哪个。

| 想干什么 | 怎么做 |
| --- | --- |
| 重新配置（改了 `CMakeLists.txt` 之后卡住） | CMake 面板的 🔄，或 **Tools → CMake → Reload CMake Project** |
| 彻底重来（改了工具链/生成器） | **Tools → CMake → Reset Cache and Reload Project** |
| 删掉构建目录 | 先**完全退出 CLion**，再删 `cmake-build-debug/`。开着 CLion 删不掉，Windows 会报"文件被占用" |
| 让 CMake 完全忘记一切 | 删 `cmake-build-debug/` **和** `.idea/`，然后 File → Open 重新打开工程 |
| 只清命令行那边 | `python tools/build.py --clean`，或者 `rm -rf build` |

**`.idea/` 该不该提交**：不该。作业仓库的 `.gitignore` 里已经有了：

```gitignore
# 编辑器
.idea/
.vscode/.cortex-debug*
*.autosave
```

### ③ 索引卡住 / 补全不工作 / 满屏假红

CLion 的索引偶尔会跟实际代码不同步，出现"这明明是对的行却标红"。

**File → Invalidate Caches → Invalidate and Restart**。

重启之后会重新建索引（几分钟）。**先试更轻的办法**：
Tools → CMake → Reload CMake Project。还不行再清缓存。

> 假红和真错的区分：**点一下 🔨 构建**。
> 构建过得去，就是索引的问题；构建过不去，那就是真错了。

### 如果没有

| 你的画面 | 原因 | 怎么办 |
| --- | --- | --- |
| 改了 File Encodings 中文还是乱 | 只改了设置，没让文件重新按新编码加载 | 关掉文件重开；或右下角编码 → Reload |
| 删 `cmake-build-debug/` 报"正在使用" | CLion 还开着 | 退出 CLion 再删 |
| Invalidate Caches 之后一直 Indexing | 正常 | 等；超过 10 分钟检查工程是不是大到离谱（我们不是） |
| 补全只补变量名，不补成员 | 索引没建完，或者这个文件不属于任何目标 | 等索引；如果是 `base/angle.cpp` 这种新文件，先加进 `CMakeLists.txt` |

---

## 看完之后

去做 **HW1**：

```bash
git clone git@github.com:<你的用户名>/EC-Training-Labs.git
cd EC-Training-Labs/day0/project
python tools/build.py
```

期望是 **`test_clamp` 通过、`test_encoder` 挂 1 个用例（3/4 passed）**。
那个失败是对的——**HW1 不要动任何代码**，HW2 才是修它。

接下来：

| 下一步 | 看哪段 |
| --- | --- |
| HW2 修 bug 时想看变量、想化简函数 | `02-4`（`Alt+F8` 求值） |
| HW3 编译与链接 | 讲义 `01` 的 `01-2`、`01-3` |
| HW4 格式化 | 讲义 `03` 全部 |
| HW5 Git 工作流 | 本讲义 `02-5` + 线下 Git 课件 |
