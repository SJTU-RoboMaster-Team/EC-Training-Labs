# 录播 01 · Keil STM32 全家桶
<!-- ⚠️ 这个文件由 lab/sync_grader.py 从 Tools/01-keil-stm32.md 复制而来。
     要改请改那份，然后重新同步 —— 不要直接改这里。 -->

> ℹ️ **这段录播还没发布。** 下面的 `🎬 视频 0X-Y · 00:00` 是分段占位符 ——
> 时间戳会在录像上线后回填。**在此之前，本文是自足的**：每一段都写了
> 「看什么、看到什么算过」，照着文字和截图走完是一样的。

| 项目 | 内容 |
| --- | --- |
| **这节讲什么** | 一个 STM32 工程由什么组成；`编译 → 链接 → .axf/.hex → 下载 → 复位运行` 这条链路上每一步发生了什么；Keil 里怎么看构建输出和 `.map`；ST-Link 下载与调试；`printf` 重定向；Keil 生成文件该不该进版本库 |
| **多长时间** | 约 34 min，分 7 段（`01-1` ~ `01-7`），每段 3–6 min |
| **对应哪份作业** | **HW3（编译与链接）——`01-2`、`01-3` 是它的直接前置**；HW0 环境自检（Keil + Pack）；HW5 Task 6（Keil 生成文件与 `.gitignore`） |

> **这节不是"Keil 使用教程"。** 菜单在哪、按钮叫什么，看一遍就会。
> 这节真正要讲清楚的是：**你敲的 `Ctrl+S` 保存的那堆文本，是怎么变成 Flash 里那串电平的**。
> HW3 让你在 `g++` 上人为制造一个 `undefined reference` 再修好，
> 那份作业的知识点全部来自 `01-2` 和 `01-3`——**先看这两段，再去做 HW3**。

> 关于本文里的输出：`g++` / `cmake` 那几段是从真实运行结果里复制的（可以直接对照）。
> Keil 的界面截图位置和构建输出是**示意**，里面的数字（大小、地址、版本号）取决于你的工程，
> 形状对上就是对的。

**分段表**（录的时候按这个切）：

| 段 | 标题 | 目标时长 |
| --- | --- | --- |
| 01-1 | 一个 STM32 工程由什么组成 | 5 min |
| 01-2 | 编译阶段：一个 `.c` 变成了什么 | 4 min |
| 01-3 | 链接阶段：`undefined reference` 为什么现在才报 | 6 min |
| 01-4 | 看懂构建输出与 `.map` 文件 | 5 min |
| 01-5 | 下载与调试：ST-Link、断点、看变量 | 5 min |
| 01-6 | `printf` 重定向：SWO 和 UART | 4 min |
| 01-7 | Keil 生成文件，以及它们该不该进版本库 | 5 min |

---

## 01-1 · 一个 STM32 工程由什么组成

> 🎬 视频 01-1 · 00:00

**做什么**：打开 `mcu/stm32f407/MDK-ARM/`，对着真实的 Keil 工程讲清楚五个组成部分。

### 先看真实仓库长什么样

```text
MasterArm/
├── app/                              业务代码（C++）
│   ├── control.cpp
│   ├── arm.cpp
│   └── ...
├── base/                             底层：电机驱动、通信、工具（C++）
│   ├── motor/driver/dji_motor_driver.h
│   └── ...
└── mcu/stm32f407/                    ★ 这一块是"和芯片绑死"的部分
    ├── .mxproject                    STM32CubeMX 的工程描述
    ├── CMakeLists.txt                同一份代码的另一套构建（GCC 工具链）
    ├── Inc/  Src/                    CubeMX 生成的 HAL 初始化代码（C）
    │   ├── main.c
    │   ├── can.c  gpio.c  tim.c ...
    └── MDK-ARM/                      ★ Keil 工程
        ├── stm32f407.uvprojx         Keil 工程文件
        ├── stm32f407.uvoptx          Keil 用户选项（调试配置、窗口状态）
        └── startup_stm32f407xx.s     启动文件
```

作业仓库里也有同样的结构，只是精简了很多：

```text
EC-Training-Labs/day0/project/
└── mcu/stm32f407/MDK-ARM/day0.uvprojx
```

> ⚠️ **作业仓库里那个 `day0.uvprojx` 是个"桩"，不要拿它编译。**
> 它里面只列了 `app` 一组两个文件，而且是**故意做成不完整**的——
> 它的用途是让你在 HW5 里看到"Keil 一打开工程就往 `MDK-ARM/` 下面写文件"这件事
> （`01-7`），不是给你练编译的。
> 真正能编译下载的 Keil 工程在战队仓库里，比如
> `MasterArm/mcu/stm32f407/MDK-ARM/stm32f407.uvprojx`。
> 这一节讲的所有东西，对着**任意一个真实的 Keil 工程**都能看。

> ⚠️ **一个反直觉的事实：真实的 STM32 工程通常有两套构建系统。**
> 上面那个 `mcu/stm32f407/` 里同时有 `CMakeLists.txt`（GCC 工具链，给 CLion / CI 用）
> 和 `MDK-ARM/*.uvprojx`（Arm 工具链，给 Keil 用）。
>
> 这是历史原因：Keil 下载调试最省事，CLion 写代码最舒服，于是两边都留着。
> **代价是加一个 `.cpp` 要改两个地方。** 忘了改其中一个，
> 就会出现"CLion 编得过、Keil 编不过"——这和 HW3 里"文件写了但没加进构建系统"
> 是**同一类错误**，只是换了个构建系统。

### 五个组成部分

**① 启动文件 `startup_stm32f407xx.s`**

这是上电后执行的**第一段代码**，用汇编写。它做的事按顺序是：

```text
① 从向量表里取出初始栈指针（SP）的值，装进 SP
② 从向量表里取出 Reset_Handler 的地址，跳过去
③ Reset_Handler 里：
   ├─ 把 .data 段从 Flash 里的初值拷贝到 RAM
   ├─ 把 .bss 段（未初始化的全局变量）在 RAM 里清零
   ├─ 调 SystemInit()          ← 配时钟树，把 16MHz 的 HSI 拉到 168MHz
   └─ 调 __main（不是你的 main）→ 由库代码完成最后的初始化，再跳到你的 main()
```

**为什么必须要有它**：Cortex-M4 上电时 RAM 里是随机值，
你的 `int counter = 0;` 这个"初值"其实是启动文件从 Flash 里拷过去的。
没有启动文件，`main()` 永远不会被调用。

**注意 `.s` 文件有两套**：Keil 用 RVDS 语法的，GCC 用另一份。
真实仓库里 `engineer/.backup/freertos/{RVDS,GCC}/ARM_CM4F/port.c` 就是这个原因——
同一个 FreeRTOS，给 Keil 和给 GCC 的是不同的移植层文件。
**换工具链不是"重新编译一下"，是换一整套和芯片绑定的底层文件。**

**② CMSIS**

CMSIS = Cortex Microcontroller Software Interface Standard，ARM 定的标准接口层。
里面是三类东西：

| 文件 | 是什么 |
| --- | --- |
| `core_cm4.h` | 内核外设的访问接口（NVIC、SysTick、MPU、ITM） |
| `stm32f407xx.h` | **寄存器定义**：`GPIOA`、`USART1` 这些名字对应哪个地址；中断号 `USART1_IRQn` 是几号 |
| `system_stm32f4xx.c` | `SystemInit()`：配时钟树、配向量表偏移 |

CMSIS 的价值是"同一份内核代码能在不同厂家的 M4 上跑"。
**`stm32f407xx.h` 是最关键的一个文件**——有了它你才能写 `GPIOA->ODR = 0x01;`，
否则你只能写 `*(volatile uint32_t*)0x40020014 = 0x01;`。

**③ 外设库**

三个选项，真实工程里你都见得到：

| 方案 | 长什么样 | 什么时候用 |
| --- | --- | --- |
| **标准库（SPL）** | `stm32f4xx_gpio.c`、`GPIO_Init()` | 老工程、教学代码。ST 早就不更新了 |
| **HAL** | `stm32f4xx_hal_gpio.c`、`HAL_GPIO_Init()` | CubeMX 生成的工程，真实仓库里的 `mcu/*/Src/` 就是这一种 |
| **直接写寄存器** | `GPIOA->BSRR = ...` | 高频路径（CAN 收发、ADC 采样）里为了省时间，会绕过 HAL |

**④ 用户代码**

`app/` 和 `base/` 这两个目录。真实仓库里全是 C++（`.cpp`）。
Keil 能编 C++（AC6 支持到 C++17），但要注意：

- 往 Keil 工程里加 `.cpp` 文件，跟加 `.c` 一样：**Group 右键 → Add Existing Files to Group**
- C 和 C++ 混编时，C 的头文件要用 `extern "C"` 包起来，否则链接时符号名对不上（见 `01-3`）

**⑤ 分散加载文件（scatter file，`.sct`）**

它告诉链接器：**哪段代码放哪块存储器**。

STM32F407VG 的存储器地图：

```text
Flash   0x08000000   1 MB     掉电不丢，代码和常量住这里
SRAM1   0x20000000   112 KB   运行时变量
SRAM2   0x2001C000   16 KB
CCM     0x10000000   64 KB    内核紧耦合，DMA 访问不了
```

Keil 默认**不让你手写**它：**Options for Target（`Alt+F7`）→ Linker** 页
勾着 `Use Memory Layout from Target Dialog`，段落布局由 **Target** 页的
`IROM1` / `IRAM1` 两个格子自动生成，编译时输出到 `Objects\day0.sct`。

要自己控制（比如把某个大数组放进 CCM，或者做 Bootloader 分区），
就取消那个勾，在 **Linker** 页指定自己的 `.sct` 文件，用 `--scatter` 传给链接器。

> **GCC 世界里的对应物是 `.ld` 链接脚本**。真实仓库里有 23 个 `.ld` 文件，
> 和 Keil 的 `.sct` 是同一个角色的两个方言。CLion 那边如果报
> `region 'RAM' overflowed`，和 Keil 报 `L6406E: No space in execution regions`
> 是同一件事。

### 你应该看到什么

打开一个真实的 Keil 工程，**Project 面板**里应该是一棵**分组树**：

```text
Project
└── stm32f407
    ├── Startup                        ← 启动文件（.s）
    ├── CMSIS                          ← core_cm4.h / system_stm32f4xx.c
    ├── Drivers                        ← HAL 或标准库
    ├── app                            ← 业务代码（C++）
    │   ├── control.cpp
    │   └── motor_monitor.cpp
    └── base
        └── ...
```

**分组名（`Startup` / `CMSIS` / `app` / `base`）是人为起的**，不同工程叫法不一样。
按 `F7` 编译一次，Build Output 里的 `compiling xxx...` 顺序就是它们被编译的顺序。

> ⚠️ **Keil 的 Group 是逻辑分组，不要求对应磁盘目录。**
> 一个 Group 里可以放着来自五个不同目录的文件；
> `Add Existing Files` 只是加了一个引用，文件还在原地，**不会拷贝**。
> 新人第一次遇到"我在 Keil 里删了一个文件，磁盘上怎么还在"就是这个原因
> ——`Remove File` 只是从工程里去掉引用。

> 💡 **作业仓库里的 `day0.uvprojx` 打开后会显示 `app` 组里有两个 `.c` 文件，
> 但那些路径是故意对不上的**（见前面的说明）。看到"文件打不开"是预期现象，
> 不是你的环境有问题。

### 如果没有

| 你的画面 | 原因 | 怎么办 |
| --- | --- | --- |
| 双击 `.uvprojx` 打开了 µVision 但里面是空的 | 文件被别的程序占用，或者工程文件本身被改坏了 | 用 **Project → Open Project** 手动选；还是空的就用 `git status` 看这个文件是不是被你改过 |
| 器件型号显示成 `Unknown Device` | DFP 没装或版本不对 | 见 `README.md` §3.6；Pack Installer 里重装 `STM32F4xx_DFP` |
| Source 文件全是灰的 / 打不开 | 文件的**相对路径**对不上（工程从别人机器上拷来的） | Options for Target → C/C++ → Include Paths 检查；或者在 Group 里 Remove 掉再加一遍 |

---

## 01-2 · 编译阶段：一个 .c 变成了什么

> 🎬 视频 01-2 · 00:00

**做什么**：点一次 **Project → Build Target**（`F7`），
然后在 Build Output 窗口里**逐行**说明每一步发生了什么。

### 编译一个文件，实际有四步

```text
control.c
   │  ① 预处理（preprocess）：处理 #include / #define / #if
   ▼
control.i        （把所有头文件的内容原地展开进来，可能几万行）
   │  ② 编译（compile）：语法分析 → 优化 → 生成汇编
   ▼
control.s
   │  ③ 汇编（assemble）：汇编 → 机器码
   ▼
control.o        ★ 目标文件：机器码 + 符号表 + 重定位表
   │
   └─ 每个 .c 都独立走一遍这条路，彼此不知道对方存在
```

Keil 的 Build Output 窗口看到的就是这个流程的日志：

```text
Build started: Project: day0
*** Using Compiler 'V6.xx', folder: 'C:\Keil_v5\ARM\ARMCLANG\Bin'
Build target 'day0'
compiling control.c...
compiling motor_monitor.c...
assembling startup_stm32f407xx.s...
```

产出物在 `Objects\` 目录里：`control.o`、`motor_monitor.o`、`startup_stm32f407xx.o`……

### 关键认知：编译器只看得到一个文件

**编译 `motor_monitor.cpp` 的时候，编译器看不到 `control.cpp`，也看不到你写的其它任何 `.cpp`。**

它能看到的东西只有：

```text
motor_monitor.cpp 本身  +  它 #include 的头文件（原地展开）
```

这就是为什么**"头文件里只有声明、没有实现"能编译通过**：
编译器没有资格判断"这个函数在别处到底有没有人写"。
它能做的全部检查是——**你调用它的方式对不对**：
参数个数、参数类型、返回类型、是不是 const。

这已经是编译器能做到的极限了。

### 现场实测：编译一个只带声明的调用

用作业工程演示。先制造 HW3 的状态：`base/math.h` 里只留一行声明。

```cpp
// base/math.h
float wrap_angle_deg(float deg);
```

`app/motor_monitor.cpp` 里调用它：

```cpp
data_.angle += wrap_angle_deg(raw_angle_deg - data_.last_raw_angle);
```

**编译这一个文件**（注意是 `-c`，只编译不链接）：

```bash
cd EC-Training-Labs/day0/project
g++ -std=c++17 -I. -c app/motor_monitor.cpp -o /tmp/mm.o
```

**你应该看到什么**：**什么都没有，退出码是 0。**

编译通过了。这时候看它的符号表：

```bash
nm -C /tmp/mm.o
```

**实测输出**：

```text
                 U wrap_angle_deg(float)
0000000000000000 T MotorMonitor::reset()
000000000000005c T MotorMonitor::reset(float)
00000000000000da T MotorMonitor::update(float, float, float)
```

**逐字读这张表**：

| 这一列 | 含义 |
| --- | --- |
| `U` | **Undefined**——这个符号在这个文件里被**用到**了，但**没有定义**。"先记一笔，等链接的时候再找" |
| `T` | 定义在 `.text` 段（也就是代码段）——这个函数在这里**真的有实现** |
| `-C` | C++ 会把 `wrap_angle_deg(float)` 修饰成 `_Z14wrap_angle_degf` 这种名字，`-C` 让 `nm` 显示回人能看的样子 |

**`U` 就是 `undefined reference` 里的那个 undefined。**
编译器早就知道这个符号没有定义，它只是**不负责解决这件事**。

### 编译错误长什么样（对照用）

把调用改成错的名字，编译就会当场报错：

```text
app/motor_monitor.cpp: In member function 'void MotorMonitor::update(float, float, float)':
app/motor_monitor.cpp:17:18: error: 'wrap_angle_degs' was not declared in this scope;
did you mean 'wrap_angle_deg'?
   17 |   data_.angle += wrap_angle_degs(raw_angle_deg - data_.last_raw_angle);
      |                  ^~~~~~~~~~~~~~
      |                  wrap_angle_deg
```

**编译错误的特征**（记住这三条，一眼就能和链接错误区分开）：

1. 开头是**文件名 + 行号 + 列号**：`motor_monitor.cpp:17:18:`
2. 关键字是 `error:` 后面跟一句语法/类型上的说明
3. 下面会画出出问题的那一行代码，用 `^` 指着具体位置

### 如果没有

| 你的画面 | 原因 | 怎么办 |
| --- | --- | --- |
| `g++: command not found` | 没装 MinGW 或不在 PATH | 见 `README.md` §3.4；或者干脆用 CLion 的内置终端 |
| `fatal error: app/motor_monitor.h: No such file or directory` | 漏了 `-I.` | `-I.` 的意思是"把当前目录也当作头文件搜索路径"，因为工程里的 `#include` 是 `"app/xxx.h"` 这种从工程根算起的写法 |
| `nm: command not found` | Git Bash 里有 `nm`，cmd 里没有 | 用 Git Bash；或者用 Keil 的 `fromelf`（见 `01-4`） |
| 编译出来一堆 warning | 正常，别忽略 | 见 `01-4` 里"warning 也是要读的" |

---

## 01-3 · 链接阶段：`undefined reference` 为什么现在才报

> 🎬 视频 01-3 · 00:00

**这一段是 HW3 的核心。** 如果只从这节里记一件事，记这一段。

### 链接器做四件事

```text
  control.o    motor_monitor.o    clamp.o    libc.a    startup.o
      │              │              │          │          │
      └──────────────┴──────────────┴──────────┴──────────┘
                              │
                  ① 合并同名段：所有 .text 拼成一整块，所有 .data 拼成一块
                  ② 符号解析：把每个 "U 符号" 在别的 .o 里找到对应的 "T 符号"
                  ③ 重定位：把"这里待填函数地址"的位置改成真实地址
                  ④ 按分散加载文件（.sct）把各段摆到 Flash / RAM 的地址上
                              │
                              ▼
                        day0.axf   （ELF 格式的可执行文件）
                              │
                    fromelf 转换（可选）
                              ▼
                    day0.hex / day0.bin   （烧录格式）
```

**①②③ 里有任何一步失败，都会报 `undefined reference` 或者 `multiple definition`。**

### 实测：链接阶段才炸

接着 `01-2` 的状态，跑一次完整构建：

```bash
python tools/build.py
```

**你应该看到什么（实测输出，只摘关键部分）**：

```text
============================================================
构建 (cmake build)
============================================================
$ cmake --build build --config Debug
[ 12%] Building CXX object CMakeFiles/day0_core.dir/app/control.cpp.o
[ 25%] Building CXX object CMakeFiles/day0_core.dir/app/motor_monitor.cpp.o
[ 37%] Building CXX object CMakeFiles/day0_core.dir/app/clamp.cpp.o
[ 50%] Linking CXX static library libday0_core.a
[ 50%] Built target day0_core
[ 62%] Building CXX object CMakeFiles/test_encoder.dir/test_encoder.cpp.o
[ 75%] Linking CXX executable test_encoder
../libday0_core.a(motor_monitor.cpp.o): in function `MotorMonitor::update(float, float, float)':
app/motor_monitor.cpp:17: undefined reference to `wrap_angle_deg(float)'
collect2: error: ld returned 1 exit status
gmake[2]: *** [tests/CMakeFiles/test_encoder.dir/build.make:98: tests/test_encoder] Error 1
```

**盯住这四行，这段视频的全部价值就在这四行里**：

| 行 | 说明 |
| --- | --- |
| `[ 25%] Building CXX object ... motor_monitor.cpp.o` | **编译成功了。**它前面没有 `error`，说明这个文件本身写得没毛病 |
| `[ 50%] Linking CXX static library libday0_core.a` → `Built target day0_core` | **静态库也链接成功了。**静态库只是把一堆 `.o` 打包成一个 `.a` 文件，**这一步不做符号解析**，所以缺实现也照样过 |
| `[ 75%] Linking CXX executable test_encoder` ← 报错在这 | 真正要生成可执行文件的时候，链接器必须把每个符号都填上地址。`wrap_angle_deg` 没人定义，填不上 |
| `collect2: error: ld returned 1 exit status` | `collect2` 是 g++ 调用真正链接器 `ld` 的外壳。**这句话本身没有信息量**——它只是在说"ld 失败了"。真正的信息在它上面那一行。MinGW 上可能显示成 `collect2.exe` |

> ⚠️ **这就是"编译期 vs 链接期"分工的最直观证据**：
> **同一个文件，编译阶段过了，链接阶段没过。**
> 如果编译器有资格判断"这个函数在别处有没有实现"，它早就在 `[25%]` 那一步拦下来了。
> 它没拦，因为它**看不到别的 `.cpp`**（`01-2` 讲过）。
>
> **分工一句话**：
> **编译器管"单个文件写对没有"，链接器管"多个文件拼起来成不成立"。**

### 一张表区分两种错误

| | 编译错误 | 链接错误 |
| --- | --- | --- |
| 谁报的 | 编译器（`armclang` / `g++` / `cl.exe`） | 链接器（`armlink` / `ld`） |
| 报错关键字 | `error: expected ...`、`was not declared`、`no matching function` | `undefined reference to ...`、`multiple definition of ...`、`ld returned 1` |
| 有没有行号 | **有**，精确到行列，还会画 `^` | 有，但常常指向"调用点"而不是"该定义的地方" |
| 一次报几条 | 一个文件里可能几十条 | 一般是几条，而且是**同一个根因** |
| 处理顺序 | 从上往下改，**改完上面下面可能自己消失** | 先看**第一个**符号名，其余的先不管 |
| 根本原因 | 这个文件的语法/类型不对 | 符号找不到定义，或者被定义了两次 |

### `undefined reference` 的四种真实原因

**① 真的没写实现。**
HW3 Task 1 就是这个状态，故意制造出来的。

**② 写了实现，但那个文件没加进构建系统。**
**这是真实项目里最常见的原因**，没有之一。

- CMake：忘了在 `add_library(day0_core ...)` 里加 `base/angle.cpp`
- Keil：忘了把 `.cpp` 加进 Group

症状完全一样：`undefined reference to 'wrap_angle_deg(float)'`。
**所以看到 `undefined reference` 的第一反应应该是两问**：

> **这个符号，定义了没有？定义了的话，那个文件加进构建了吗？**

**③ 签名不匹配。**
C++ 会把参数类型编进符号名。声明是 `wrap_angle_deg(float)`，
实现写成 `wrap_angle_deg(double)`，链接器就会报：

```text
undefined reference to `wrap_angle_deg(float)'
```

**注意括号里的参数类型——那就是线索。** 报的是 `(float)` 但你实现的 `(double)`，
编译器帮你做了隐式转换的是编译期的事，链接期它们就是两个不同的符号。

**④ C 和 C++ 混编，忘了 `extern "C"`。**

```cpp
// C 的头文件被 C++ 包含时
#ifdef __cplusplus
extern "C" {
#endif

void can_send(uint8_t* data, uint32_t len);

#ifdef __cplusplus
}
#endif
```

不写会报 `undefined reference to 'can_send(unsigned char*, unsigned int)'`，
但对方明明定义了 `can_send`。原因：C++ 会把函数名修饰成 `_Z8can_sendPhj`，
而 C 编译出来的符号就叫 `can_send`，两边对不上。
**这在 Keil 工程里特别常见**，因为 HAL 是 C，业务代码是 C++。

### `multiple definition` 也顺便说一下

```text
multiple definition of `wrap_angle_deg(float)'; first defined here
```

**原因**：两个 `.o` 里都定义了同一个符号。最常见的写法错误是
**在头文件里写了非 `inline` 的函数定义**，然后这个头文件被两个 `.cpp` include：

```cpp
// base/math.h   ✗ 错误写法：每个 include 它的 .cpp 都会生成一份定义
float wrap_angle_deg(float deg) {
  ...
}

// base/math.h   ✓ 正确写法之一：加 inline
inline float wrap_angle_deg(float deg) {
  ...
}
```

这也正是 HW2 里 `deg_normalize_180` 为什么写成 `inline` 的原因，
以及 HW3 做法 B 为什么可以"留在头文件里"——**加了 `inline` 就不会重复定义**。

### 如果没有

| 你的画面 | 原因 | 怎么办 |
| --- | --- | --- |
| 报的是 `deg_normalize_180` 而不是 `wrap_angle_deg` | 只删了 `math.h` 里的实现，没改 `motor_monitor.cpp` 的调用点 | 一样是链接错误，改完调用点即可。HW3 里说明了这种情况也算完成 |
| 报错里还有 `undefined reference to 'main'` | 你在手动链接一堆 `.o`，忘了带那个有 `main` 的文件 | 用 `python tools/build.py` 走完整构建，别手动拼 |
| 明明加了文件还是报错 | 加文件之后**没有重新配置 CMake** | CLion：**Tools → CMake → Reload CMake Project**；命令行：`python tools/build.py --clean` |
| 报 `ld: cannot find -lxxx` | 这是**找不到库文件**，不是找不到符号 | `-l` 后面那个名字是库名，检查库路径 `-L` |

---

## 01-4 · 看懂构建输出与 `.map` 文件

> 🎬 视频 01-4 · 00:00

**做什么**：按 `F7` 编译，然后**竖着**读 Build Output 的每一行；
再打开链接器写的 `.map`，从里面找三样东西。

### Build Output 窗口要竖着读

**你应该看到什么**：一段完整的构建日志，最后两行分别是
`Program Size: Code=... RO-data=... RW-data=... ZI-data=...`
和 `".\Objects\xxx.axf" - 0 Error(s), 0 Warning(s).`（warning 数可能是 0，也可能不是）。

```text
Build started: Project: stm32f407
*** Using Compiler 'V6.xx', folder: 'C:\Keil_v5\ARM\ARMCLANG\Bin'
Build target 'stm32f407'
compiling control.cpp...
compiling motor_monitor.cpp...
compiling main.c...
linking...
Program Size: Code=24812 RO-data=1884 RW-data=164 ZI-data=5312
".\Objects\stm32f407.axf" - 0 Error(s), 3 Warning(s).
Build Time Elapsed:  00:00:06
```

（这是**示意**，数字是你的工程实际值。）

| 这一行 | 它在说什么 |
| --- | --- |
| `*** Using Compiler 'V6.xx'` | 这次用的是哪个编译器版本。**报编译错误时先看这一行**——AC5 和 AC6 的报错风格完全不同 |
| `compiling xxx...` | 每个源文件单独走一遍 `01-2` 那四步。**只列出来的文件会被编译**——你的新文件没出现在这里，就是没加进工程 |
| `linking...` | 所有 `.o` 交给链接器，走 `01-3` 那四步 |
| **`Program Size: Code=... RO-data=... RW-data=... ZI-data=...`** | ★ 这一段下面单独讲 |
| `0 Error(s), 3 Warning(s)` | **warning 也要读**，见下 |
| `Build Time Elapsed` | 编译耗时。改一行代码全量重编要几分钟的话，说明依赖关系没配好 |

### `Program Size` 那四个数

```text
Program Size: Code=24812 RO-data=1884 RW-data=164 ZI-data=5312
                 ↑         ↑          ↑           ↑
              机器码    只读数据   有初值的变量  零初始化的变量
```

| 项 | 里面是什么 | 占哪块存储器 |
| --- | --- | --- |
| `Code` | 你写的所有函数，编译出来的机器码 | Flash |
| `RO-data` | Read-Only data：`const` 变量、字符串字面量、常量查表 | Flash |
| `RW-data` | Read-Write data：**有初值**的全局 / 静态变量 | **Flash 和 RAM 都占** |
| `ZI-data` | Zero-Initialized：**没写初值**（或者初值为 0）的全局 / 静态变量 | RAM |

算占用的两个公式：

```text
Flash 占用 ≈ Code + RO-data + RW-data
RAM   占用 ≈ RW-data + ZI-data
```

**为什么 `RW-data` 两边都算**：它在 Flash 里存着一份**初值**，
上电后由启动文件把它拷到 RAM 里（就是 `01-1` 里启动文件做的第 ③ 步）。
所以 Flash 里要有位置放初值，RAM 里也要有位置放运行时的那一份。

对一下 STM32F407VG 的容量（Flash 1 MB，主 SRAM 128 KB）：
上面这个工程 Flash 用了约 27 KB，RAM 用了约 5.5 KB——**离满还远得很**。
等到某天你看到 `L6406E: No space in execution regions`，就是这两个数里有一个撞墙了。

### warning 一定要读

嵌入式里的 warning 有相当一部分是**真 bug 的前兆**：

```text
warning: #1-D: last line of file ends without a newline   ← 就是 clang-format 那条 InsertNewlineAtEOF
warning: #177-D: variable "speed" was declared but never referenced
warning: #223-D: function "clampf" declared implicitly     ← C 里忘了 include，参数类型可能被猜错
warning: #1295-D: Deprecated declaration ...               ← 老代码里的隐患
```

老工程师的习惯是"**0 Error, 0 Warning 才算编译过**"。
Day 0 不要求你做到这一点，但**至少每次都要把 Build Output 从头扫一遍**——
尤其是你刚加了新文件、刚换了编译器版本的时候。

**想只编译当前打开的文件**：**Project → Translate**（`Ctrl+F7`）。
但注意：**改了 `.h` 之后不要只 Translate**。头文件被改动，所有
`#include` 它的 `.c/.cpp` 都要重新编译，只 Translate 当前文件会漏掉别人——
用 `F7` 让它自己算依赖。

### `.map` 文件：链接器写的账单

**怎么让它生成**：

**Options for Target（`Alt+F7`）→ Listing** 页 → **Linker Listing** 那一栏勾上
**`Memory Map`**（想更全就再加 `Symbols`）→ 重新 `F7` 编译一次。

生成的文件在：

```text
Listings\stm32f407.map
```

> ⚠️ **改动 Listing 选项之后必须重新编译**，`.map` 是链接时生成的。
> 另外：**链接失败的时候不会生成新的 `.map`**——
> 你在 HW3 制造 `undefined reference` 之后看到的 `.map` 是上一次成功的那个，
> 别拿它当"链接过了"的证据。

`.map` 里有三个部分值得你会看。

#### ① `Image component sizes`：谁把 Flash 吃掉了

```text
Image component sizes

      Code (inc. data)   RO Data    RW Data    ZI Data      Debug   Object Name
      1240         48        256         12        512        8324   control.o
       860         32        128          4        256        5012   motor_monitor.o
       412         16         64          0        128        2044   clamp.o
      2104         96        384         16        768       13336   Object Totals
```

用法：加了一个库之后 Flash 突然紧张，就在这张表里按 `Code` 排序找元凶。
**注意 `Debug` 那一列不算进 Flash**（调试信息不进芯片），别被它吓到。

#### ② `Memory Map of the image`：每个东西被放在哪个地址

```text
    Exec Addr    Load Addr    Size         Type   Attr      Idx    E Section Name        Object
    0x08000000   0x08000000   0x00000188   Data   RO            3    RESET               startup_stm32f407xx.o
    0x08000188   0x08000188   0x00000c40   Code   RO         1234    .text               control.o
    0x20000000   0x08000c48   0x00000010   Data   RW         2345    .data               motor_monitor.o
    0x20000010   0x20000010   0x00000200   Data   ZI         3456    .bss                control.o
```

| 列 | 意思 |
| --- | --- |
| `Exec Addr` | **运行时**的地址 |
| `Load Addr` | **存在 Flash 里**的地址 |
| `Type` / `Section Name` | `.text` 是代码，`.data` 是有初值变量，`.bss` 是零初始化变量，`RESET` 是向量表 |
| `Object` | 这一段来自哪个 `.o` |

**看 `.data` 那一行**：`Exec Addr = 0x20000000`（RAM），`Load Addr = 0x08000c48`（Flash）
——两个地址不一样，这就是 `RW-data` 两边都占的**直接证据**。

**另一个用法**：想确认"我写的那个函数到底有没有被链接进去"，就在这张表里搜函数名。
**搜不到就是没进去**——和 HW3 里"文件没加进构建系统"的症状互为印证。

#### ③ `Global Symbols`：符号地址表

设备跑飞（HardFault）的时候，调试器里能读到 `PC` / `LR` 寄存器的值，
比如 `0x08000A3C`。把这个地址拿到 `Global Symbols` 里查，
就知道**崩在哪个函数、哪一行**。

**这是排查现场问题最有用的一招**，比打印一百行日志都快。

#### 顺便：反汇编

```bash
"C:\Keil_v5\ARM\ARMCLANG\bin\fromelf.exe" --text -c -s -o Objects\day0.dis.txt Objects\day0.axf
```

生成的 `dis.txt` 里每条机器指令都带着自己的地址，配合 `.map` 一起看。
GCC 那边的对应命令是 `objdump -d`。**这个不是必须会的，知道有就行。**

### 如果没有

| 你的画面 | 原因 | 怎么办 |
| --- | --- | --- |
| 勾了 `Memory Map` 但 `Listings\` 里没有 `.map` | 没重新编译 | 改完选项重新 `F7`；`.map` 只在链接时生成 |
| `.map` 里搜不到我写的函数 | 那个文件没被链接进可执行文件 | 检查 Group（Keil）或 `add_library`（CMake）——**HW3 的同一类问题** |
| `Program Size` 里 `ZI-data` 大得离谱 | 有一个巨大的全局数组 | 到 `Image component sizes` 里按 `ZI Data` 排一下，找出是哪个 `.o` |
| 编译输出里 warning 一堆，不知道哪个要管 | 老工程的历史遗留 | 先看你**刚改过的文件**有没有 warning；别人的遗留问题记下来，不要顺手一起改 |
| `fromelf: command not found` | 不在 PATH 上 | 用完整路径调用（上面那条命令就是完整路径）；或者干脆跳过这一步 |

---

## 01-5 · 下载与调试：ST-Link、断点、看变量

> 🎬 视频 01-5 · 00:00

**做什么**：**Options for Target（`Alt+F7`）→ Debug** 配 ST-Link，
下载、打断点、单步、看变量、看寄存器。

### 配置调试器

**`Alt+F7` → Debug** 页：

| 位置 | 填什么 | 说明 |
| --- | --- | --- |
| 右上角下拉框 | `ST-Link Debugger` | 用 ULINK 选 ULINK；用 J-Link 要先装 J-Link 的 Keil 支持包 |
| 右边 **Settings** → Debug 页 | `Port: SW`（不是 JTAG） | SWD 只占 SWDIO + SWCLK 两根线，省引脚 |
| 同页 | `Max Clock: 1MHz` | **连不上就往下调**：1MHz → 500kHz → 100kHz。线长、杜邦线质量差的时候，降速是万能药 |
| **Flash Download** 页 | 勾 `Reset and Run` | 不勾的话，下载完芯片停在复位状态，你会以为"程序没跑"——其实是没让它跑 |
| 同页 | `Programming Algorithm` 里应有 `STM32F4xx Flash` (1M) | 没有就是 DFP 没装好（见 `README.md` §3.6） |
| **Trace** 页 | 见 `01-6`（SWO 用） | 只用 UART 的话不用动 |

### 下载 ≠ 调试

| 按钮 | 快捷键 | 做什么 |
| --- | --- | --- |
| **Flash → Download** | `F8` | 只烧录，不进调试。烧完按板子上的复位键就跑 |
| **Debug → Start/Stop Debug Session** | `Ctrl+F5` | 烧录 **+** 进入调试会话（能打断点、看变量） |

**"下载 → 复位 → 运行"这条链的完整含义**：
把 `.axf` 里的各段按地址写进 Flash → 让 CPU 从 `0x08000000` 取出向量表 →
跳到 `Reset_Handler` → 启动文件做数据搬运 → `SystemInit()` 配时钟 → `main()`。

**验证下载成功**：Build Output 窗口会打印

```text
Load "C:\\...\\Objects\\day0.axf"
Erase Done.
Programming Done.
Verify OK.
Application running ...
```

**看到 `Verify OK` 就是写进去了。** 只有 `Programming Done` 没有 `Verify OK`，
说明写进去了但校验没过——通常是 Flash 算法选错或者供电不稳。

### 断点

在代码行左边的灰色边框上点一下，出现红点。`Ctrl+F5` 进调试后程序会停在那里。

**⚠️ Cortex-M4 的硬件断点只有 6 个。** 你在 `openocd` 的输出里会看到
`hardware has 6 breakpoints, 4 watchpoints`——就是它。
第 7 个断点**不会报错，只是不生效**。调试时发现"这个断点怎么不停"，
先数一下自己打了几个。

**条件断点**：右键红点 → **Breakpoint...** → 在 `Expression` 里填条件，
比如 `speed_dps > 100.0f`。调试一个 1kHz 的控制循环时，
普通断点会停在第一万次循环上，条件断点才能停在你关心那一帧。

**单步的四个键**：

| 操作 | Keil 快捷键 | 区别 |
| --- | --- | --- |
| Step Over | `F10` | 执行这一行，函数调用**整个跳过** |
| Step Into | `F11` | 进入被调用的函数 |
| Step Out | `Ctrl+F11` | 从当前函数里跑出去，回到调用者 |
| Run | `F5` | 跑到下一个断点 |

### 看变量

| 窗口 | 菜单 | 用来干什么 |
| --- | --- | --- |
| Watch 1 / 2 | **View → Watch Windows → Watch 1** | 把变量名敲进去（或从代码里拖过来），单步时它一直更新。**调 PID 的时候就靠它** |
| Call Stack | **View → Call Stack Window** | 看"是谁调过来的"。HardFault 的时候第一眼看这里 |
| Registers | **View → Registers Window** | R0–R15、LR、PC、xPSR |
| Memory | **View → Memory Windows → Memory 1** | 按地址看内存，查缓冲区越界 |
| 外设寄存器 | **Peripherals → System Viewer → GPIOA / TIM1 ...** | 图形化看外设寄存器，依赖 DFP 里的 `.svd` 文件。**这是 Keil 相对 CLion 最实用的功能** |

**变量显示成 `<not in scope>` 或者值明显不对**，八成是优化等级的问题：

**Options for Target → C/C++ → Optimization** 设成 `Level 0 (-O0)`。

> ### 为什么调试构建一定要关优化
>
> 编译器开启优化之后会做这些事：把变量一直放在寄存器里（内存里那个副本就不更新了）、
> 把两条语句合并成一条指令、把整个函数 inline 掉、把没用的分支删掉。
>
> 后果：
> - 你在 Watch 窗口里看到的变量值是**过期的**
> - 你在 `if` 那一行打的断点，实际停在**另一行**
> - 单步走起来"跳来跳去"
>
> 这跟 HW4 里 clang-format 那条 `AllowShortIfStatementsOnASingleLine: Never`
> 是**同一件事的两个面**：`if (x) return;` 写在一行，
> 一个断点对应两条语句，调试器没法告诉你要停在哪一条。
> 一个是**编译期**别合并语句，一个是**源码**别合并语句，目标都是——
> **让一行源码对应一条可断点的指令**。
>
> 真实工程的做法：**Debug 和 Release 是两个 Target**，
> 在 `Options for Target` 右上角的 `Target:` 下拉框里切换，
> Debug 用 `-O0` + 完整调试信息，Release 用 `-O2` / `-Os`。

### `01-5` 你应该看到什么

```text
① Ctrl+F5 后，µVision 从编辑模式切到调试模式（菜单栏多出 Debug/Peripherals/Flash）
② 代码窗口左边出现黄色箭头，指着当前停在的那一行
③ 底部出现 Command 窗口，里面是调试器的命令历史
④ Watch 窗口里敲进去的变量名有了值
```

### 如果没有

| 你的画面 | 原因 | 怎么办 |
| --- | --- | --- |
| `No ST-Link detected` | 驱动没装 / 线没插好 / 被别的软件占用 | 设备管理器看有没有 `STLink dongle`；关掉 STM32CubeProgrammer 之类的软件（它会独占调试器）；见 `README.md` §3.7 |
| `Error: Flash Download failed - Target DLL has been cancelled` | 调试器连上了但芯片没响应 | ① 板子供电了吗 ② 降 SWD 时钟到 100kHz ③ Debug 页把 `Connect` 改成 `under Reset`（芯片里跑着个把 SWD 引脚复用掉的程序时用这招） |
| `RDDI-DAP Error` | SWD 通信不稳 | 换短的杜邦线；确认 SWDIO/SWCLK/GND 三根都接了；确认没有把 SWD 引脚配成普通 GPIO |
| 断点打上了但不停 | 断点超过 6 个 / 优化把代码改掉了 | 数断点数量；把优化设成 `-O0` |
| 变量显示 `<optimized out>` | 同上，优化等级太高 | 设 `-O0` |
| 程序一下载就跑飞 | `Reset and Run` 勾了但你的代码有 bug | 取消 `Reset and Run`，改成手动复位，在 `main` 第一行打断点 |

---

## 01-6 · printf 重定向到串口：SWO 和 UART

> 🎬 视频 01-6 · 00:00

**做什么**：让 `printf` 真的能输出到 PC。讲两种接法，说清各自的代价。

### 先说为什么不能直接用 printf

PC 上 `printf` 写到 stdout，MCU 上**没有 stdout 这个东西**。
标准库提供了一条退路叫 **semihosting（半主机）**：固件通过调试器
向 PC 发请求，让 PC 帮忙打印。

**半主机有三个致命问题**：

1. **脱离调试器就死**——因为要调试器在背后做系统调用。拔掉调试器程序就卡住
2. 极慢——每一次 `printf` 都是一次调试器往返
3. 发布固件里带着它，别人一烧就发现程序不动

所以嵌入式里要**把 `printf` 的输出重定向到一条真实的物理通道**。

### 方案 A · SWO / ITM（一根线，不用额外接线）

Cortex-M3/M4/M7 内核里有一个 **ITM**（Instrumentation Trace Macrocell），
能把字符从芯片"推"到调试器，走的是调试口上多出来的一根 **SWO** 引脚。

**代码**（加在 `main.c` 或任意一个 `.c` 里）：

```c
#include <stdio.h>

int fputc(int ch, FILE *f) {
  ITM_SendChar((uint32_t)ch);
  return ch;
}
```

`ITM_SendChar` 在 CMSIS 的 `core_cm4.h` 里就有，不用额外装库。

**Keil 这边要配**：`Alt+F7` → **Debug → Settings → Trace** 页

| 选项 | 填什么 |
| --- | --- |
| `Core Clock` | 168 MHz（STM32F407 的主频，填错就是乱码） |
| `SWO Clock` | 2 MHz（先填小一点，能出字再往上加） |
| `Trace Enable` | 勾上 |
| `ITM Stimulus Port` | 勾 `0`（`ITM_SendChar` 默认走端口 0） |

**看输出**：**View → Serial Windows → Debug (printf) Viewer**。

**你应该看到**：

```text
hello from STM32, tick=1
hello from STM32, tick=2
```

**如果没有**：

| 画面 | 原因 | 怎么办 |
| --- | --- | --- |
| 窗口是空的 | Trace 没勾 / `Core Clock` 填错 | 回 Trace 页检查；把 SWO Clock 降到 1MHz 试 |
| 全是乱码 | 时钟填错 | `Core Clock` 必须是芯片真实主频；用 HSE 还是 HSI 会影响实际频率 |
| 什么都没有，但调试正常 | **你的调试器没有 SWO 引脚** | 山寨 ST-Link V2 小U盘**没有 SWO**。换 ST-Link V2-1（Nucleo 板载）或 V3，或者改用方案 B |

**SWO 的代价**：带宽很小（正常也就几 KB/s 的有效文本），
发多了会**静默丢字**——不报错，就是少了几行。打日志可以，传数据不行。

### 方案 B · UART（两根线 + USB-TTL）

**代码**：

```c
#include <stdio.h>
#include "stm32f4xx.h"

int fputc(int ch, FILE *f) {
  while ((USART1->SR & USART_SR_TXE) == 0) {
  }
  USART1->DR = (uint8_t)ch;
  return ch;
}
```

**接线（新人最容易错的地方）**：

```text
STM32 的 PA9  (USART1_TX) ────→ USB-TTL 的 RX
STM32 的 PA10 (USART1_RX) ←──── USB-TTL 的 TX
STM32 的 GND              ────  USB-TTL 的 GND      ← 这根不能省
```

**TX 接 RX、RX 接 TX——是交叉的。** 接成 TX→TX 的话什么都不会发生，
而且不会有任何报错，纯靠肉眼查。

PC 端用串口助手（或 CLion 的 Serial Monitor 插件），
波特率和代码里初始化 USART 时设的**必须一致**（常用 115200，8N1）。

**UART 的优点**：不依赖调试器。**下载完拔掉调试器，插着 USB-TTL 就能看输出**——
跑车调试的时候这一点非常重要。缺点是占一个外设和两根线，而且要用掉一个 USB 口。

### 方案 C · RTT（战队实际在用的，了解一下）

**SEGGER RTT (Real-Time Transfer)** 的思路：调试器直接在 RAM 里读写一块环形缓冲区，
固件只管往缓冲区里写。好处是**不占外设、不用额外接线、比 SWO 快得多**，
而且不打断实时性（写缓冲区是纯内存操作）。

真实仓库里就有现成的配置：

```text
engineer/.config/openocd.cfg               ← OpenOCD 连板子
engineer/.config/openocd_rtt_proxy.cfg     ← 把 RTT 缓冲区代理出来
```

J-Link 有现成工具（RTT Viewer / Ozone）；ST-Link 走 OpenOCD 也能用。
**Day 0 不要求你会用**，知道你将来会从 `printf` 升级到它就行——
真跑起车来，SWO 那点带宽是不够的。

### 三种方案对比

| | SWO / ITM | UART | RTT |
| --- | --- | --- | --- |
| 占几根线 | 复用调试线（多一根 SWO） | 额外 2 根 + USB-TTL | 复用调试线，零额外引脚 |
| 对调试器的要求 | 必须支持 SWO（山寨 ST-Link V2 不支持） | 任意 | J-Link 原生，ST-Link 走 OpenOCD |
| 拔掉调试器还能看吗 | ❌ | ✅ | ❌ |
| 速度 | 低（会静默丢字） | 取决于波特率 | 高 |
| 上手成本 | 中 | 低 | 高 |

### 一个必须知道的坑

**`printf` 里带 `%f` 会让固件体积暴涨**（浮点格式化代码要几 KB），
而且 `printf` **不是可重入的**——如果在中断里 `printf`，会把主循环正在打印的
半行内容冲掉，输出看起来像被撕碎了。

战队真实代码里一般不直接用 `printf`，而是自己写一个极简的 log 宏
（只支持整数和字符串，或者干脆只打一个 ID）。这个认知够用了。

**编译报 `_sys_exit` / `_sys_write` / `_ttywrch` undefined**：
这是半主机那一套没被裁掉。

- AC6：`Options for Target → Target` 勾 **Use MicroLIB**（用精简版 C 库）
- 或者加 `__asm(".global __use_no_semihosting\n\t");` 明确告诉链接器"我不要半主机"

---

## 01-7 · Keil 生成文件，以及它们该不该进版本库

> 🎬 视频 01-7 · 00:00

**做什么**：先看现象、看清单，再落成 `.gitignore` 规则，
最后说清"`.uvprojx` 到底提不提交"。**这一段是 HW5 Task 6 的背景。**

### 现象：`git status` 里冒出一堆陌生文件

Keil 打开一次工程、调一次试、拖一下面板，就会在 `MDK-ARM/` 下面写东西。
作业仓库里给了一个脚本，专门把这件事模拟出来（你现在不用开着 Keil 就能看到）：

```bash
cd EC-Training-Labs/day0/project
python tools/make_generated_files.py
git status
```

**你应该看到**：`Untracked files` 里多了三个：

```text
Untracked files:
  (use "git add <file>..." to include in what will be committed)
	mcu/stm32f407/MDK-ARM/DebugConfig/day0_STM32F407VG.dbgconf
	mcu/stm32f407/MDK-ARM/RTE/_day0/RTE_Components.h
	mcu/stm32f407/MDK-ARM/day0.uvguix.zhangsan
```

**这三个文件不该进版本库。** 下面解释为什么。

### 清单：谁写的、里面是什么、会不会变

| 文件 / 目录 | 谁写的 | 里面是什么 | 会变吗 | 进版本库吗 |
| --- | --- | --- | --- | --- |
| **`*.uvprojx`** | 建工程的人 / 你在 Keil 里加删文件的时候 | 目标芯片型号、**文件列表**、include 路径、宏定义、优化等级、用的调试器、依赖的 Pack 版本 | 只在真的改了工程配置时变 | ✅ **该进** |
| `*.uvoptx` | µVision 自己 | 你打开了哪些文件、窗口布局、**断点**、调试器端口/时钟、上次烧录的设置 | 几乎每次打开都变 | ❌ 不该进 |
| `*.uvguix.<用户名>` | µVision 自己 | 纯窗口布局（哪个面板多宽），**文件名里带用户名** | 拖过面板就变 | ❌ 不该进 |
| `DebugConfig/` | µVision 自己 | `.dbgconf`，调试器配置 | 换调试器/改设置就变 | ❌ 不该进 |
| `RTE/` | Run-Time Environment 组件管理器 | `RTE_Components.h`，以及从 Pack 里拷进来的组件源码 | 打开工程时可能重新生成 | ❌（本仓库约定：`**/RTE/**`） |
| `Objects/` | 编译器 / 链接器 | `.o`、`.axf`、`.hex`、`.lnp`、`.build_log.htm` | 每次编译 | ❌ 构建产物 |
| `Listings/` | 链接器 | `.map`、`.lst`、`.htm` | 每次编译 | ❌ 构建产物 |

### 为什么 `*.uvoptx` 比 `*.uvprojx` 改得还频繁

这是个反直觉的观察，用真实仓库的数据说：

| 文件 | 在历史里被改动的次数 |
| --- | --- |
| `.../mcu/stm32f407/MDK-ARM/stm32f407.uvoptx` | **127 次** |
| `MasterArm/mcu/stm32h723/MDK-ARM/stm32h723.uvoptx` | 46 次 |
| `MasterArm/mcu/stm32h723/MDK-ARM/stm32h723.uvprojx` | 42 次 |
| `controller/mcu/stm32f407/MDK-ARM/stm32f407.uvprojx` | 20 次 |

**`.uvoptx` 是"用户选项"**，名字里的 `opt` 指的是"**你的**选项"，
不是"工程的选项"。打开过哪些文件、断点打在哪、调试器用多快的时钟——
每个人都不一样，所以每个人每次打开都会写一次。

**`.uvprojx` 是"工程选项"**，只在真的动了工程结构时才应该变。
它变得少，是因为**它本来就该变得少**。

### 加起来的代价

- 三个仓库的去重历史里，`.uvprojx` 有 25 个文件、`.uvoptx` 有 25 个文件进过版本库
- 我们统计过战队几个仓库的**合并冲突**，Keil 的 `*.uvprojx` / `*.uvoptx` 占了约 **15%**
- 而且这种冲突**没有任何信息量**：两个人改了同一个 XML 文件里相隔三行的两个 `<File>` 节点，
  Git 说"冲突了"，你要手工把两段 XML 拼起来——拼错了 Keil 还打不开工程

**这就是"生成文件不该进库"最实在的理由**：它带来的冲突是纯粹的负担，
不会带来任何收益。

### `.gitignore` 该写什么

作业仓库里 `day0/project/.gitignore` 已经有构建产物那一部分了：

```gitignore
# 构建目录
build/
cmake-build-*/
__pycache__/
*.pyc

# 构建产物（按文件类型）
*.o
*.elf
*.hex
*.map
*.bin
*.axf
```

**缺的是 Keil 那几种。** 补上（这三条是真实仓库 `.gitignore` 里的原文）：

```gitignore
# Keil 生成文件
*DebugConfig*
**/RTE/**
*uvguix*
```

真实项目通常还会再加构建产物那几条：

```gitignore
# Keil 构建产物
Objects/
Listings/
*.lnp
*.build_log.htm
*.dep
```

**验证**：

```bash
git status
```

**你应该看到**：`mcu/` 下面那三个文件从 untracked 列表里**消失了**。

> `*uvguix*` 和 `*DebugConfig*` 前后都带 `*`，是因为
> `uvguix` 后面还跟着用户名（`day0.uvguix.zhangsan`），
> 而 `DebugConfig` 可能是 `Objects/xxx.DebugConfig` 这种形式。
> **ignore 规则是被人一条条踩坑补出来的，不是一次写全的**——
> 你在 HW5 里补的这三条，和当年战友补的是同样的三条。

### 那 `*.uvprojx` 到底提不提交？

**提交。不提交它，别人 clone 下来根本打不开这个工程。**

正确做法不是"不提交"，而是——**只在真的改了工程配置时才提交，并且说清改了什么**：

```bash
git add mcu/stm32f407/MDK-ARM/stm32f407.uvprojx
git diff --staged
git commit -m "chore(mdk): add base/angle.cpp to the Keil project"
```

**不要"顺手把工程文件一起提交"**。因为一次 `git add .` 带上来的 `uvprojx` 里，
常常混着你本地的调试器型号改动、优化等级改动、Pack 版本改动——
这些跟你这次的功能没关系，但会实打实地影响别人的构建。

> **为什么优化等级的变化很危险**：你在本地把 `-O0` 改成了 `-O3` 调性能，
> 顺手提交了工程文件。别人拉下来之后，
> 编译体积变了、断点打不准了、某些 `volatile` 没写对的地方行为变了——
> 而 diff 里只有一行 XML，谁也不会去看。

> `*.uvoptx` 也有团队选择提交，想把调试器配置共享出去。
> **两种做法都能自洽，但必须全队统一。** 这个仓库的约定是**不提交**。

### 已经提交进去了怎么办

```bash
# 从版本库里移除，但保留本地文件（--cached 是关键）
git rm --cached mcu/stm32f407/MDK-ARM/stm32f407.uvoptx
git commit -m "chore(mdk): stop tracking Keil user options"
```

> ⚠️ **`git rm` 不带 `--cached` 会把文件从磁盘上删掉。**
> 删掉的是 Keil 的窗口布局还好，删掉 `.uvprojx` 就得重新配工程。
> 敲之前先 `git status` 看清楚。

补上 `.gitignore` 之后，`git rm --cached` 过的文件不会再出现在 `git status` 里。

### 如果没有

| 你的画面 | 原因 | 怎么办 |
| --- | --- | --- |
| 补了 `.gitignore` 那三个文件还在 untracked 里 | 它们**已经被提交过**了 | `.gitignore` 只对未跟踪的文件生效，已跟踪的要用 `git rm --cached` |
| `python tools/make_generated_files.py` 报错 | 工作目录不对 | 必须在 `day0/project/` 下跑，脚本按相对路径找 `mcu/` |
| 想撤销这次模拟 | —— | 那三个文件没被跟踪过，直接删掉目录即可；或者 `git clean -n` 看一眼再 `git clean -f mcu/`（**先 `-n` 预览，别直接 `-f`**） |

---

## 附：这一节的速查表

**编译 / 链接**

| 报错 | 阶段 | 第一反应 |
| --- | --- | --- |
| `error: expected ';'` / `was not declared` | 编译 | 改语法，看行号 |
| `undefined reference to 'X'` | 链接 | **X 定义了没有？定义了的话，那个文件加进构建了吗？** |
| `multiple definition of 'X'` | 链接 | 头文件里是不是写了非 `inline` 的函数定义 |
| `L6406E: No space in execution regions` | 链接 | RAM/Flash 不够，看 `.map` 的 `Image component sizes` |
| `collect2: error: ld returned 1 exit status` | —— | 这句本身没信息，**看它上面一行** |

**Keil 菜单**

| 想干什么 | 路径 |
| --- | --- |
| 编译 | `F7` |
| 只编译当前文件 | **Project → Translate**（`Ctrl+F7`） |
| 全部重编 | **Project → Rebuild all target files** |
| 工程选项 | **Options for Target**（`Alt+F7`） |
| 装/管 Pack | **Project → Manage → Pack Installer** |
| 下载 | **Flash → Download**（`F8`） |
| 进调试 | **Debug → Start/Stop Debug Session**（`Ctrl+F5`） |
| 看变量 | **View → Watch Windows → Watch 1** |
| 看调用栈 | **View → Call Stack Window** |
| 看外设寄存器 | **Peripherals → System Viewer → ...** |
| 看 printf 输出 | **View → Serial Windows → Debug (printf) Viewer** |
| 生成 `.map` | **Options for Target → Listing → Linker Listing → Memory Map** |

**文件进不进库**

| 进 | 不进 |
| --- | --- |
| `*.uvprojx`（只在真改配置时） | `*.uvoptx`、`*.uvguix.*`、`DebugConfig/`、`RTE/`、`Objects/`、`Listings/` |

---

## 看完之后

去做 **HW3**。那份作业会让你在 `day0/project` 上亲手制造一个
`undefined reference`，再把它修好。

做完 HW3 你应该能不看讲义回答这三个问题：

1. 编译阶段和链接阶段分别在做什么？各自输入什么、输出什么？
2. `undefined reference` 是哪个阶段的错误？为什么编译 `motor_monitor.cpp` 的时候不报？
3. 你最后是怎么修的？为什么那样能解决？

答不上来就回 `01-2` 和 `01-3` 各看一遍——**这两段加起来 10 分钟**。
