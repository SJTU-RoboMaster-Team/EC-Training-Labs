# HW0 · 环境自检

> **这份在课上当堂做完**，不占课下时间。它不计分，但**不过这一关，后面全都做不了**。

六条命令 + 两项界面检查。全过就截图交。

---

## 学习目标

1. 把做后面所有作业要用的东西装齐、验通
2. 学会「装完一项立刻验一次」这个习惯 —— 后面配工具链、配调试器都是这个套路
3. 遇到装不上的时候，知道去哪儿找（这份任务书末尾）

---

## 开始之前

- [ ] 一台自己的电脑（Windows 优先，本培训按 Windows 写）
- [ ] 能连上网（下载量大约 3–5 GB，Keil 和 CLion 占大头）

> **装之前先说三句话，这三条能省掉你后面几小时的玄学问题：**
>
> 1. **全部装默认路径**（`C:\Keil_v5`、`C:\Program Files\Git`）。
>    改到 D 盘、或者路径里带中文和空格，后面工具链配置会多出一堆奇怪的报错。
> 2. **检查你的用户名和路径里有没有中文和空格**（`C:\Users\张三`）。
>    已经有的改起来麻烦，但要知道：CMake 和 OpenOCD 在这类路径下都可能报
>    看起来完全无关的错。实在改不了就先记下，卡住了找助教。
> 3. **装 Keil 和 ST-Link 驱动之前，先关掉杀毒软件的实时防护**，装完再打开。
>    这是「装到一半失败」的第一大原因。

---

## 要装的东西

按依赖顺序装。**每装完一项就立刻验一次**，不要全装完再一起验 ——
出问题的时候你不知道是哪一项的锅。

| # | 装什么 | 在哪 | 备注 |
| --- | --- | --- | --- |
| ① | **Git for Windows** | <https://git-scm.com/download/win> | 一路默认，**默认编辑器选 VS Code 或 Notepad++，不要留 Vim** |
| ② | **Python 3** | <https://www.python.org/downloads/> | 装的时候**勾上 Add python.exe to PATH** |
| ③ | **CMake** | <https://cmake.org/download/> | 选 `Windows x64 Installer`，装的时候勾 **Add CMake to the system PATH** |
| ④ | **Ninja** | <https://github.com/ninja-build/ninja/releases> → `ninja-win.zip` | 解压出 `ninja.exe` 放进 `C:\Program Files\CMake\bin\`（和 cmake 放一起，那个目录已经在 PATH 里了） |
| ⑤ | **MinGW-w64**（g++） | 见下面「编译器怎么装」 | CLion 自带的那个也行 |
| ⑥ | **CLion** | <https://www.jetbrains.com/clion/> | 用**学生认证**免费，别直接买 |
| ⑦ | **Keil MDK** | <https://www.keil.com/demo/eval/arm.htm> | 装完还要单独装 **STM32F4 Device Family Pack** |
| ⑧ | **ST-Link 驱动** | ST 官网 | 只有要烧板子的组才需要 |

> **为什么 ③④ 要一起装**：Windows 上如果没装 Visual Studio，CMake 会默认挑
> **NMake** 生成器 —— 而 `nmake` 只在 VS 的「开发者命令提示符」里才有。
> 普通终端里会报 `'nmake' 不是内部或外部命令`，或者更迷惑的
> `CMAKE_CXX_COMPILER not set`，**完全不指向真正的原因**。
> 装了 Ninja 就不一样了：CMake 会优先用它。
>
> **为什么 ⑦ 装完还要装 Pack**：Keil 本体不带任何芯片的支持文件。
> 不装 Pack 的话，新建工程时设备列表里找不到 STM32F4，
> 编译会报找不到 `stm32f4xx.h`。

### 编译器怎么装（⑤）

两条路，选一条：

**省事**：不单独装，直接用 CLion 自带的那套 MinGW。
装完 CLion 之后，在它的 Terminal 里敲 `g++ --version`，有输出就行。

**正规**：装 MSYS2（<https://www.msys2.org/>），装完在 MSYS2 终端里：

```bash
pacman -S mingw-w64-x86_64-gcc mingw-w64-x86_64-ninja
```

然后把 `C:\msys64\mingw64\bin` 加进系统 PATH。

> 后面 HW1–HW5 和 cpp1–cpp4 都只用 `g++` 编译，不用交叉编译工具链。
> `arm-none-eabi-gcc`（编 STM32 固件用的）**这份培训不需要**，
> 想在 CLion 里编 MCU 固件的话另外问助教。

---

## 任务

### Task 1 · Git 装好并配身份

```bash
git --version
```

**你应该看到**（版本号会更新，`.windows.1` 是关键）：

```text
git version 2.47.1.windows.1
```

配身份：

```bash
git config --global user.name "Zhang San"
git config --global user.email "zhangsan@example.com"
git config --global --list
```

**这两项会写进你以后每一条 commit**。写错了历史里就永久留着错的身份 ——
它跟的是提交，不是账号。

### Task 2 · 配 SSH Key

```bash
ssh-keygen -t ed25519 -C "you@sjtu.edu.cn"
```

一路回车，密码可以留空。

```bash
cat ~/.ssh/id_ed25519.pub
```

复制输出的**整行**，粘到 GitHub：头像 → **Settings** → **SSH and GPG keys**
→ **New SSH key**。

验证：

```bash
ssh -T git@github.com
```

**你应该看到** `Hi <你的用户名>! You have successfully authenticated...`

> ⚠️ 粘的是 **`.pub` 结尾的公钥**，不是 `id_ed25519` 那个私钥。
> 搞反了是最常见的错。

### Task 3 · 六项自检

**依次敲一遍，然后整屏截图。**

```bash
git --version
cmake --version
g++ --version
python --version
clang-format --version      # 没有输出不算失败，见下
ssh -T git@github.com
```

**怎么算过：**

| | 期望 |
| --- | --- |
| `git --version` | 有版本号，带 `.windows.1` |
| `cmake --version` | 有版本号，**3.16 以上** |
| `g++ --version` | 有版本号。没有就回上面「编译器怎么装」 |
| `python --version` | 有版本号。报「不是内部或外部命令」见常见错误 |
| `clang-format --version` | **大部分人是没有的，这不影响 HW4** —— CLion 自带一份。有输出更好，没有就在截图里空着 |
| `ssh -T git@github.com` | `Hi <你的用户名>! ...` |

> **`clang-format` 这条别去装。** 后面 HW4 要的是「在 IDE 里格式化」，
> CLion 内置的那份读的也是工程里的 `.clang-format` 配置。
> 单独装一个命令行版对你没用。

### Task 4 · 两项界面检查

命令行之外，还有两项要看界面：

- [ ] **Keil µVision** 能打开 → `Pack Installer` 里 **STM32F4xx_DFP** 是 `Installed`
- [ ] **CLion** 能打开 `EC-Training-Labs/day0/project` 这个目录，且 CMake 面板**没有红字**

> CLion 那一项**现在还不一定能过** —— 你还没 clone 仓库。
> 先打开 CLion 确认它能启动、能新建工程就行；等 HW1 拿到仓库再回来验这一条。

---

## 自查

**这份作业没有 grader**（它验的是你机器上的环境，不是仓库里的东西）。
验收方式就是**截图**：

```bash
# 六项自检，整屏截图
git --version && cmake --version && g++ --version && python --version && clang-format --version && ssh -T git@github.com
```

> 最后那条 `ssh -T` 会失败退出（GitHub 不提供 shell），
> 用 `&&` 串起来的话后面的不会执行 —— 所以**一条一条敲，然后整屏截图**。

---

## 提交

把下面三样发到飞书群：

1. **六项自检的整屏截图**
2. **Keil 的 Pack Installer 截图**（能看到 STM32F4xx_DFP 是 Installed）
3. 如果哪一项没装上，**单独说一句**（比如「clang-format 没有，用 CLion 的」）

---

## 评分

**不计分。** 六项自检全过（`clang-format` 除外）、两项界面检查过了就算完成。

---

## 常见错误

| 症状 | 原因 | 怎么办 |
| --- | --- | --- |
| `'git' 不是内部或外部命令` | 装完**没重开终端** | 关掉所有终端窗口重开（PATH 是启动时读的） |
| `python` 打开的是应用商店 | Windows 的商店别名 | 设置 → 应用 → 高级应用设置 → 应用执行别名 → 关掉 `python.exe` |
| `'cmake' 不是内部或外部命令` | 装的时候没勾 Add to PATH | 重装，勾上；或者手动把 `C:\Program Files\CMake\bin` 加进 PATH |
| `cmake` 报 `nmake` 找不到 | 生成器选了 NMake | 装 Ninja（见上表 ④），然后 `cmake -G Ninja ...` |
| `cmake` 报 `CMAKE_CXX_COMPILER not set` | 同上，真正原因是生成器 | 同上 |
| `ssh -T` 报 `Permission denied (publickey)` | 公钥没贴 / 贴了私钥 / 贴到别的账号 | 见 Task 2 的警告；用 `ssh -vT git@github.com` 看它用了哪个 key 文件 |
| Keil 里找不到 STM32F4 | 没装 Device Family Pack | Pack Installer 里装 `Keil.STM32F4xx_DFP` |
| Keil 装到一半失败 | 杀毒软件拦了 | 关实时防护重装，装完再打开 |
| 路径里有中文，CMake 报奇怪的错 | `C:\Users\张三` | 建一个英文名的本地账户，或者找助教 |

装不上的情况远不止这些。**带上报错原文**去问 —— 别只说「装不上」，
那对助教没有任何信息量。

---

## 参考

| 内容 | 在哪 |
| --- | --- |
| Git 基本命令（课上跟做） | Day 0 Git 课件「跟做」章节 |
| Keil 怎么用（工程结构、编译下载调试） | [`../notes/01-keil-stm32.md`](../notes/01-keil-stm32.md) |
| CLion 怎么配（工具链、CMake、调试） | [`../notes/02-clion-setup.md`](../notes/02-clion-setup.md) |
| clang-format 怎么配 | [`../notes/03-clang-format.md`](../notes/03-clang-format.md) |

---

## 做完之后

环境通了，`git --version` 和 `ssh -T` 都有输出 —— 后面所有作业都建立在这上面。

下一步是 **HW1**：clone 你自己的仓库，把工程构建起来。
