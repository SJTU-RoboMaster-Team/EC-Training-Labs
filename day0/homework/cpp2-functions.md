# cpp2 · 函数与参数传递

> C++ 线第二份。上一份是 `cpp1`（声明与定义）。

这份练习的代码量比 `cpp1` 小得多 —— 一个函数、十来行。但它考的是
**顺序**：限幅和类型转换谁先谁后。写反了程序照样编译、照样跑，只是结果不对。

---

## 学习目标

1. 能说清参数**按值传**和按 `const` 引用传的区别，知道什么时候用哪个
2. 知道浮点转整数是**截断**，不是四舍五入
3. 知道"先限幅再转换"和"先转换再限幅"的结果不一样

---

## 开始之前

- [ ] 做完了 `cpp1`（`math.cpp` 的四个函数都写好了）
- [ ] 读过讲义 **§7b.1–7b.3**（函数放在哪、参数怎么传、默认参数）
- [ ] 讲义 **§6c.3**（类型转换）也扫过一眼

> `cpp2` 要用 `cpp1` 写的 `math::limit`。没做完 `cpp1` 会编不过。

---

## 获取代码

```bash
cd EC-Training-Labs/day0/cpp
git switch main && git pull
```

---

## 背景：限幅和转换，谁先谁后

真实仓库里每个电机都有控制量上限，由型号决定：

| 型号 | 控制量范围 |
| --- | --- |
| M3508 | `[-16384, 16384]` |
| M2006 | `[-10000, 10000]` |
| GM6020 | `[-30000, 30000]` |

`Motor::setTorque(float target_torque)` 收一个浮点的目标转矩，
返回**整数**的控制量。所以要经过两步：

```text
   目标转矩(float)  →  限幅到型号范围  →  转成 int16_t  →  发给电调
```

**问题来了：这两步能换顺序吗？**

假设目标转矩是 `1e9`（某个计算炸了，飞出来一个巨大的数），上限是 16384：

| 顺序 | 过程 | 结果 |
| --- | --- | --- |
| 先限幅再转 | `1e9` → 夹到 `16384.0f` → `static_cast<int16_t>` | `16384` ✅ |
| 先转再限幅 | `static_cast<int16_t>(1e9f)` → ??? | **不可预期** ❌ |

第二行为什么不可预期：`static_cast` 把一个**超出目标类型范围**的浮点数转成整数，
在 C++ 标准里是**未定义行为**。你可能得到 `0`、可能得到 `-1`、可能得到任何东西，
换个编译器或者换个优化等级结果就变了。

> **这不是理论问题。** 控制代码里出现 `NaN` 或者飞出范围的数很常见
> （除零、传感器没数据、参数没初始化）。限幅就是拿来兜这种事的 ——
> 但前提是它得在转换**之前**。

---

## 任务

### Task 1 · 看一眼要改的地方

打开 `base/motor/motor.cpp`，找到 `Motor::setTorque`：

```cpp
int16_t Motor::setTorque(float target_torque) {
  // TODO(cpp2)：见头文件里的说明。
  (void)target_torque;
  intensity_ = 0;
  return intensity_;
}
```

头文件 `base/motor/motor.h` 里写了四条要求，**先读一遍再动手**。

### Task 2 · 想清楚参数为什么是按值传的

```cpp
int16_t setTorque(float target_torque);      // ← 按值传
```

讲义 §7b.2 给过判断顺序。这里三条都指向"按值传"：

- 不需要改调用方的变量
- `float` 只有 4 字节，**拷贝一下比解引用还快**（引用本质是指针，多一次内存访问）
- 真实仓库里 `math::limit(float, float, float)` 也是全按值传的

**别改成 `const float&`。** 验收会用 `static_assert` 检查这一条 ——
不是因为引用错了，是因为这个场合按值传更合适。

### Task 3 · 实现它

要做四件事：

1. 拿到这个型号的上限（`intensityLimit(type_)` 已经有了）
2. 把 `target_torque` 限幅到 `[-上限, +上限]` —— 用 `cpp1` 写的 `math::limit`
3. **限幅之后**再 `static_cast<int16_t>`
4. 存进 `intensity_` 并返回

> 记得 `#include "base/common/math.h"`。这个文件现在只 include 了 `motor.h`。

### Task 4 · 重新构建，跑测试

```bash
cmake --build build
ctest --test-dir build --output-on-failure
```

**期望：** `test_motor` 全过。里面有两条专门测这个顺序：

- `1e9` 应该夹到 `16384`（M3508 的上限）
- `-1e9` 应该夹到 `-16384`

还有两条测**截断**：`1.9f` 出来是 `1`，`-1.9f` 出来是 `-1`。
浮点转整数是往零的方向截断，不是四舍五入 —— 这个和限幅顺序无关，但要知道。

### Task 5 · 顺手确认没把 `cpp1` 弄坏

```bash
ctest --test-dir build --output-on-failure
```

`test_math` 也还在跑。全绿再提交。

### Task 6 · 提交

```bash
cd ../..
git add day0/cpp/base/motor/motor.cpp
git commit -m "feat(motor): clamp the torque before narrowing to int16_t"
git push
```

---

## 自查

```bash
python tools/grade.py cpp2 .
```

**期望看到：**

```text
┌────────────────────────────────────────────────────────────┐
│ C++02 · 函数与参数传递                                     │
├────────────────────────────────────────────────────────────┤
│ ✅ 能构建                 cmake 配置 + 编译通过            │
│ ✅ test_motor 全过        motor 12/12                      │
│ ✅ setTorque 签名没改     契约成立（探针编译通过）         │
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
- [ ] `test_motor` 全部用例通过
- [ ] `tests/` 下的测试文件**没有被修改**
- [ ] 历史里有**你自己写的提交**
- [ ] `setTorque` 的签名没改（`int16_t setTorque(float)`）
- [ ] commit message 符合 `type(scope): subject`
- [ ] commit message 不是废话（`update` / `修改` 这类不合格）

---

## 常见错误

| 症状 | 原因 | 怎么办 |
| --- | --- | --- |
| `1e9` 那条挂了 | 先转换后限幅 | 把 `static_cast` 挪到限幅后面 |
| `1.9f` 期望 `2` 但得到 `1` | 浮点转整数是截断 | 题目就要求截断，不用改 |
| 编译报找不到 `math::limit` | 没 include | 加 `#include "base/common/math.h"` |
| 编译报 `math::limit` 未定义 | `cpp1` 没做完 | 先回去把 `math.cpp` 写了 |
| 签名检查挂了 | 改成了 `const float&` | 改回按值传（讲义 §7b.2） |
| 限幅方向写反 | 上限传成了正数当 `min` | `math::limit(v, -lim, +lim)`，注意负号 |

---

## 参考

| 内容 | 在哪 |
| --- | --- |
| 参数按值还是按引用 | 讲义 **§7b.2** |
| 默认参数 | 讲义 §7b.3 |
| 类型转换的三种写法 | 讲义 §6c.3 |
| 真实仓库里的 `limit` / `limitMin` / `deadBand` | 讲义 §7b.2 |

---

## 做完之后

下一份 `cpp3` 做状态机：枚举、`switch`，还有指针数组 —— 那才是战队代码里
最常见的形状（`Motor* arr[11]`）。
