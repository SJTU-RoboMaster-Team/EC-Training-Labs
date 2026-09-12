# C++ 基础 · 练习工程

这里是一个**精简过的固件工程**。它不是一个玩具例子 —— 它的分层、命名、
注释风格都是从战队两个真实仓库里抽象出来的：

| 这个工程 | 抽象自 |
| --- | --- |
| `base/common/math.cpp` | `Wheel-Legged-Robot-2026/base/common/math.cpp` |
| `base/motor/dji_motor_driver.*` | `Wheel-Legged-Robot-2026/base/motor/driver/dji_motor_driver.*` |
| `base/motor/motor.*` | `Wheel-Legged-Robot-2026/base/motor/motor.*` |
| `app/chassis.*` | `Wheel-Legged-Robot-2026/app/wheel_legged_chassis.*` + `RM2026-Dual-Arm-Engineer/MasterArm/app/arm.h` |

每个文件里都写了出处（`文件:行号`），讲义的「真实仓库」小节里抄了原文。

**这一套和 HW1–HW5 相互独立。** 编号 `cpp1`–`cpp4`，共用同一份验收工具。

---

## 先读讲义

```text
lecture.md      自学讲义（两万多字，带自测题）
```

**不要直接开始改代码。** 讲义是按"读代码时会卡在哪"组织的，
每一节都指了它在真实仓库里的对应位置。每份练习要读哪几节，
讲义 §0.4 有一张表。

---

## 四份练习

| 练习 | 改哪个文件 | 做什么 | 先读 |
| --- | --- | --- | --- |
| `cpp1` | `base/common/math.cpp` | 实现四个数学函数 | §3、§6.7 |
| `cpp2` | `base/motor/motor.cpp` | `Motor::setTorque`：**先限幅、再转整数** | §7b.1–7b.3、§6c.3 |
| `cpp3` | `app/chassis.cpp` | 状态机 + 模式名 | §8.3、§6b |
| `cpp4` | `base/motor/dji_motor_driver.cpp` | 解析 / 打包 CAN 报文 | §6c |

代码里搜 `TODO(cpp` 就能找到全部要改的地方 ——
在 IDE 里按 `Ctrl+Shift+F` 全局搜索（CLion / VS Code 都是这个键）。

**顺序有依赖**：`cpp3` 的 `Chassis::update` 要调 `cpp2` 写好的 `Motor::setTorque`。
所以按 cpp1 → cpp2 → cpp3 做，`cpp4` 什么时候做都行。

---

## 怎么构建和自查

```bash
# 在你仓库的根目录下（就是 EC-Training-Labs/ 这一层）

# ① 构建 + 跑测试
cd day0/cpp
cmake -S . -B build               # 配置失败再加 -G（见下）
cmake --build build
ctest --test-dir build --output-on-failure

# ② 用验收工具自查（和老师用的是同一份代码）
cd ../..
python tools/grade.py cpp1 .
python tools/grade.py --list      # 看还有哪些练习
```

> **配置就失败的话，是生成器没选对**（Windows 上最常见）。
> 试 `-G Ninja`（装了 Ninja）或 `-G "MinGW Makefiles"`（装了 MinGW）；
> 换生成器前要先删掉 `build/`。详见 `../notes/02-clion-setup.md` §2。

**第一次构建会失败**，报的是：

```text
undefined reference to `math::limit(float, float, float)'
```

这不是环境坏了 —— `math.cpp` 里还没有实现。**这条报错就是第一课**
（讲义 §3.5）。看懂它，比背下来有用。

---

## 验收标准

只有 PASS / FAIL。每份练习的必修项：

| 练习 | 必修项 |
| --- | --- |
| `cpp1` | 能编译 · `test_math` 全过 · 四个函数都有实现 · **四个函数签名没改** · 测试文件未被修改 · 你自己有提交 · commit message 格式 |
| `cpp2` | 能编译 · `test_motor` 全过 · 测试文件未被修改 · 你自己有提交 · `setTorque` 签名没改 · commit message 格式 |
| `cpp3` | 能编译 · `test_chassis` 全过 · 测试文件未被修改 · 你自己有提交 · `test_motor` 没被改坏 · commit message 格式 |
| `cpp4` | 能编译 · `test_can` 全过 · 测试文件未被修改 · 你自己有提交 · **不许出现 `double`** · 浮点返回 `float` · commit message 格式 |

**「签名没改」是怎么验的**：不是读你的代码猜，而是拿一小段 `static_assert`
和你的头文件一起编译。编译过了就说明契约成立；编译不过时你会看到
`static_assert` 里写给人的那句话 —— **报错信息本身就是讲义**。

**「不许出现 `double`」不是风格偏好**：战队两个工程都只开单精度 FPU
（`-mfpu=fpv4-sp-d16` / `-mfpu=fpv5-sp-d16`），`double` 会退化成软件模拟。
实测战队自己的 70822 行代码里 `float` 出现 5233 次，`double` **0 次**。

---

## 改测试让它通过 = 任务没完成

`tests/` 下的测试文件是**题面**，不是你的代码。
验收工具会比对测试文件的哈希，改了就判 FAIL。

---

## 遇到问题

1. 先看讲义里对应那一节
2. 再跑一遍 `python tools/grade.py cppN .`，它会告诉你是哪一条没过
3. 还不行，带着 `python tools/grade.py cppN .` 的完整输出和
   `git log --oneline -5` 去问
