# cpp4 · 位运算与 CAN 打包

> C++ 线最后一份。前面是 `cpp1` / `cpp2` / `cpp3`。

这份讲怎么把几个字节拆开、再拼回去。它是 **Day 3 CAN 课的前置** ——
那边讲协议（哪几个字节是什么、什么单位），这边讲手上怎么操作。

---

## 学习目标

1. 会用移位和掩码把 `int16` 拆成两个字节、再拼回来
2. 知道**大端**是按什么顺序摆字节的
3. 知道 `struct` 不能直接拿来映射协议报文（对齐会插 padding）
4. 知道为什么这个工程里一个 `double` 都不许有

---

## 开始之前

- [ ] 做完了 `cpp1`–`cpp3`
- [ ] 读过讲义 **§6c**（位运算、类型转换、定长类型、结构体布局）
- [ ] 知道 `uint8_t` / `int16_t` 这些定长类型是什么（讲义 §6c.5）

---

## 获取代码

```bash
cd EC-Training-Labs/day0/cpp
git switch main && git pull
```

---

## 背景：8 个字节里塞了四个电机的控制量

DJI 的电调（C620）用一帧 CAN 报文控制最多四个电机。协议规定：

```text
控制帧：ID = 0x200，DLC = 8

  DATA[0] DATA[1] | DATA[2] DATA[3] | DATA[4] DATA[5] | DATA[6] DATA[7]
  └─ 电机 1 ─┘      └─ 电机 2 ─┘      └─ 电机 3 ─┘      └─ 电机 4 ─┘
     2 字节            2 字节            2 字节            2 字节
```

每个电机占 2 字节，**高字节在前**（大端）。所以：

```text
DATA[0] = 控制量 >> 8        ← 高 8 位
DATA[1] = 控制量 & 0xFF      ← 低 8 位
```

反过来，收到反馈帧时把两个字节拼回去：

```text
控制量 = (DATA[0] << 8) | DATA[1]
```

**就是这两行。** 整份练习剩下的内容，是把这件事做对。

> 真实仓库里这段代码在
> `wheel-legged/base/motor/driver/dji_motor_driver.cpp:63`，
> 讲义 §6c.2 抄了原文。它用的写法略有不同 —— 看完这份练习可以回去对照。

---

## 任务

### Task 1 · 先看要改的两个函数

打开 `base/motor/dji_motor_driver.cpp`：

- `parseRawData(const uint8_t data[8])` —— 把 8 字节解成 `RawData`
- `packControl(const int16_t intensity[4], uint8_t out[8])` —— 把 4 个控制量打成 8 字节

头文件 `base/motor/dji_motor_driver.h` 里有完整的字段表，**先读那张表**。

### Task 2 · 想清楚有符号怎么处理

`RawData` 里有三个**有符号**字段：

```cpp
struct RawData {
  uint16_t ecd = 0;              // 编码器值(0~8191) —— 无符号
  int16_t rotate_speed_rpm = 0;  // 转速(rpm) —— 有符号！
  int16_t torq_current = 0;      // 转矩电流 —— 有符号！
  uint8_t temp = 0;              // 温度 —— 有符号？看协议
};
```

拼的时候如果写成 `(data[2] << 8) | data[3]` 直接赋给 `int16_t`，
负数会出问题。正确做法是**先拼成 `uint16_t`，再转 `int16_t`**：

```cpp
static_cast<int16_t>(static_cast<uint16_t>(data[2]) << 8 | data[3])
```

为什么：负数的补码表示里，最高位是 1。先按无符号拼出完整的 16 位，
再让 `static_cast<int16_t>` 按补码解释它，就是那个负数。

> 中间那些 `static_cast` 不是啰嗦。`data[2]` 是 `uint8_t`，参与运算会先
> **整型提升**成 `int`（讲义 §6c.4），`<< 8` 之后类型是 `int`；
> 直接赋给 `int16_t` 会触发窄化警告。

### Task 3 · 实现 `parseRawData`

按头文件里那张字段表，逐字段用移位和掩码拼出来。

**别用 `memcpy` 把 8 个字节直接盖到结构体上。** 原因见下。

### Task 4 · 想清楚为什么不能用 `memcpy` 盖

看起来这样最省事：

```cpp
RawData d;
memcpy(&d, data, sizeof(RawData));   // ← 不要这么写
```

**因为编译器会在结构体成员之间插 padding（填充）**，让每个成员落在对齐的地址上。
`RawData` 这 4 个成员凑巧是 8 字节、没错位 —— 但那是**运气**。
换个字段顺序就错位了：

```cpp
struct Bad { int8_t a; int32_t b; int8_t c; };   // sizeof = 12，不是 6
//                   ↑ 前面被插了 3 字节 padding
```

协议报文是紧凑的 8 个字节，没有 padding。用 `memcpy` 盖上去，等于赌
"编译器的布局和协议一致" —— 这个赌以后一定会输。

**正确做法就是逐个字段用位运算拼**，也就是 Task 3。

### Task 5 · 实现 `packControl`

反过来：把 `intensity[i]` 拆成 `out[2i]`（高字节）和 `out[2i+1]`（低字节）。

提示（这一步有坑）：

```cpp
const uint16_t raw = static_cast<uint16_t>(intensity[i]);   // ← 先转无符号！
out[2 * i]     = static_cast<uint8_t>(raw >> 8);
out[2 * i + 1] = static_cast<uint8_t>(raw & 0xFF);
```

**为什么要先转 `uint16_t`**：`intensity[i]` 可能是负数。
对**有符号负数**做右移，补进来的是 0 还是 1 由实现决定（讲义 §6c.1）。
先转成无符号，`>>` 的行为就是确定的。测试里专门有两组负数
（`-2` 和 `-30000`）。

### Task 6 · 构建 + 跑测试

```bash
cmake --build build
ctest --test-dir build --output-on-failure
```

**期望：** 四个测试全过。

`test_can` 会验：

- 一帧 `{0x12,0x34, 0xFF,0x9C, 0x00,0xFA, 42, 0x00}` 解出来是
  `ecd=0x1234`、`rpm=-100`、`current=250`、`temp=42`
- 打包 `{0x1234, 0x0102, -2, -30000}` 得到的 8 个字节逐个对

### Task 7 · 顺手确认没把前面的弄坏

四个测试都要绿。`cpp1`–`cpp3` 的成果还在同一个工程里。

### Task 8 · 提交

```bash
cd ../..
git add day0/cpp/base/motor/dji_motor_driver.cpp
git commit -m "feat(can): parse and pack C620 frames with bit operations"
git push
```

---

## 自查

```bash
python tools/grade.py cpp4 .
```

**期望看到：**

```text
┌────────────────────────────────────────────────────────────┐
│ C++04 · 位运算与 CAN 打包                                  │
├────────────────────────────────────────────────────────────┤
│ ✅ 能构建                 cmake 配置 + 编译通过            │
│ ✅ test_can 全过          can 12/12                        │
│ ✅ 不出现 double          两个工程都是单精度 FPU…          │
│ ✅ degNormalize180 返回 float  契约成立（探针编译通过）    │
│ ✅ message 格式           1/1 条合规                       │
├────────────────────────────────────────────────────────────┤
│ 结论   PASS                                                │
└────────────────────────────────────────────────────────────┘
```

---

## 提交

把自查输出截图发到飞书群。

---

## 评分

**只有 PASS / FAIL。** 必须全部通过：

- [ ] 能构建
- [ ] `test_can` 全部用例通过
- [ ] 工程里**没有出现 `double`**
- [ ] `degNormalize180` 的返回类型仍是 `float`
- [ ] commit message 符合 `type(scope): subject`

### 为什么「不许出现 double」是必修项

不是风格偏好，是硬约束。

战队两个工程都是**单精度 FPU**：

```text
wheel-legged/mcu/stm32f407/CMakeLists.txt   -mfpu=fpv4-sp-d16
dual-arm/MasterArm/mcu/stm32h723/...        -mfpu=fpv5-sp-d16
```

`-sp-` 就是 single precision。`double` 在这两块板子上没有硬件支持，
会退化成**软件模拟** —— 一次除法就是几十条指令。

实测战队自己的 70822 行代码：`float` 出现 5233 次，`double` **0 次**。
所以验收会扫一遍源码，出现 `double` 就判 FAIL。

> 扫描会先剥掉注释和字符串 —— `// 这里不能用 double` 这种注释不算违规。

---

## 常见错误

| 症状 | 原因 | 怎么办 |
| --- | --- | --- |
| `parse rpm` 挂了，得到正数 | 先拼成 `int16_t` 了 | 先拼 `uint16_t` 再 `static_cast<int16_t>` |
| `pack[4] pack[5]` 负数那两个挂了 | 负数直接右移 | 先 `static_cast<uint16_t>` |
| 编译报窄化警告 | `hi << 8` 是 `int` | 显式 `static_cast<uint16_t>` |
| 自查说"不出现 double"挂了 | 某个中间变量写成了 `double` | 改成 `float`；确认字面量带 `f` |
| `temp` 解出来是负数 | 用 `uint8_t` 接了 | 看协议字段表里给的类型 |
| 打包顺序反了 | 低字节放前面了 | 协议是**高字节在前**，`out[2i]` 是高字节 |
| 四个测试只过了 `test_can` | 前面几份被改坏了 | 一起看，`cpp1`–`cpp3` 也要绿 |
| `ctest` 找不到 `test_*` | 构建没成功 | 先看 `cmake --build build` 的输出 |

---

## 参考

| 内容 | 在哪 |
| --- | --- |
| 六个运算符与三个套路 | 讲义 **§6c.1** |
| 真实仓库怎么打包的 | 讲义 **§6c.2** |
| 类型转换的三种写法 | 讲义 §6c.3 |
| 整型提升、有符号无符号 | 讲义 §6c.4 |
| 定长类型 `<cstdint>` | 讲义 §6c.5 |
| 结构体布局、为什么不能 `memcpy` | 讲义 **§6c.6** |
| C620 协议本身（字节序、ID 规则、单位） | **Day 3 · CAN 课** |

---

## 做完之后

C++ 线四份练习到这里结束。回头看一遍你做过的：

| | 练的什么 |
| --- | --- |
| `cpp1` | 声明与定义 —— 那条 `undefined reference` |
| `cpp2` | 函数与参数 —— 限幅和窄化的顺序 |
| `cpp3` | 枚举、`switch`、指针 —— 状态机 |
| `cpp4` | 位运算 —— 拆装字节、`struct` 对齐 |

这四样是读战队代码最常撞到的东西。剩下的（模板、虚函数、异常、
动态分配那一堆）讲义里都讲过，用到的时候回去翻就行。

**下一步**：Day 3 的 CAN 课。你会看到今天写的这套拆装字节的写法，
出现在真实的电机驱动代码里。
