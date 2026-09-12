# cpp3 · 枚举、switch 与指针

> C++ 线第三份。前面是 `cpp1`（声明与定义）、`cpp2`（函数与参数）。

这份要写一个**状态机**。代码量比前两份大一点，但套路在战队代码里到处都是：
一个枚举表示"现在处于什么模式"，一个 `switch` 决定"这个周期干什么"。

---

## 学习目标

1. 会用 `enum class` 表达状态，并让 **`switch` 覆盖每一个值**
2. 知道为什么**不要**给 `switch` 写 `default`
3. 会写"指针 + 长度"表示的数组（战队代码里的主流写法）

---

## 开始之前

- [ ] 做完了 `cpp1` 和 `cpp2`
- [ ] 读过讲义 **§8**（枚举与 `enum class`）、**§8.3**（`switch` 覆盖枚举）
- [ ] 讲义 **§6b**（指针）也看过

> `cpp3` 的状态机要调 `cpp2` 写好的 `Motor::setTorque`。前面的没做完会编不过。

---

## 获取代码

```bash
cd EC-Training-Labs/day0/cpp
git switch main && git pull
```

---

## 背景：为什么最后一个 `case` 不写 `default`

`app/chassis.h` 里定义了四种工作模式：

```cpp
enum class Mode : uint8_t {
  kIdle = 0,
  kSpin,       // 小陀螺
  kFollow,     // 跟随
  kCalibrate,  // 标定
};
```

给这种枚举写 `switch` 时，有两种写法：

```cpp
// 写法 A：写完所有 case，不留 default
switch (m) {
  case Mode::kIdle:      return "kIdle";
  case Mode::kSpin:      return "kSpin";
  case Mode::kFollow:    return "kFollow";
  case Mode::kCalibrate: return "kCalibrate";
}
return "?";

// 写法 B：写几个，剩下的交给 default
switch (m) {
  case Mode::kIdle: return "kIdle";
  case Mode::kSpin: return "kSpin";
  default:          return "?";
}
```

**写法 A 更好，原因是以后。** 假设半年后有人往 `Mode` 里加了一个 `kPush`：

- 写法 A：编译器在**这里**报一条警告，说 `kPush` 没处理。加枚举的人当场就知道
  还有别的地方要改
- 写法 B：新值悄悄走进 `default`，返回 `"?"`。没有任何报错，直到某天调试时
  发现日志里一堆问号

> 这就是"让编译器替你查漏"。**能用类型系统拦住的问题，不要留到运行期。**

最后那个 `return "?"` 还是要写的 —— 编译器不知道 `switch` 已经穷举了所有可能，
少了它会报"函数可能没有返回值"。这是 `-Wall -Wextra` 下的行为。

---

## 任务

### Task 1 · 看清单里要改的两处

```bash
python tools/grade.py cpp3 .        # 先看它现在报什么
```

要改的都在 `app/chassis.cpp`，两个函数：

- `modeName(Mode m)` —— 枚举转字符串
- `Chassis::update()` —— 每个控制周期调一次

头文件 `app/chassis.h` 里写了每个模式该做什么。

### Task 2 · 实现 `modeName`

四个模式各返回一个字符串：`"kIdle"` / `"kSpin"` / `"kFollow"` / `"kCalibrate"`。

**用完所有 `case`，不要写 `default`。** 理由见上面。

### Task 3 · 想清楚 `Chassis` 存的是什么

```cpp
class Chassis {
 private:
  motor::Motor* wheels_;      // ← 指针
  int wheel_count_;           // ← 长度
  ...
};
```

**这是一对**。战队代码里几乎不写 `std::vector<Motor>` —— 固件里不动态分配，
数组都是在别处（`interface/` 那一层）建好的，这里只存一个首地址和长度。

所以遍历要自己写：

```cpp
for (int i = 0; i < wheel_count_; ++i) {
  wheels_[i].setTorque(...);
}
```

> `wheels_[i]` 等价于 `*(wheels_ + i)` —— 指针加偏移再解引用。
> 语法糖而已，不用怕。

### Task 4 · 实现 `Chassis::update`

规则在头文件里，四句话：

| 模式 | 每个轮子的转矩 |
| --- | --- |
| `kIdle` | `0` |
| `kSpin` | `spin_torque_`（1.0） |
| `kFollow` | `follow_torque_`（0.5） |
| `kCalibrate` | `0`，而且**不能因为"堵转"中断** |

返回值是这一周期四个轮子控制量的**和**（测试用它判断"到底有没有输出"）。

> `kCalibrate` 那一条是多出来的要求：标定时轮子会顶到限位，那不是堵转。
> 现在这份代码里还没有阻力判断，先把值给对就行。

**测一下你的理解**：`kFollow` 的转矩是 `0.5`，转成 `int16_t` 是 `0`
（截断，和 `cpp2` 一样）。所以 `kFollow` 下四个轮子的输出和是 **0** ——
测试里就是这么期望的。别以为这是 bug。

### Task 5 · 构建 + 跑测试

```bash
cmake --build build
ctest --test-dir build --output-on-failure
```

**期望：** `test_chassis` 和 `test_motor` 都全过。

`test_chassis` 会验 `modeName` 的四个返回值，以及四种模式下的 `update()` 返回和。

### Task 6 · 提交

```bash
cd ../..
git add day0/cpp/app/chassis.cpp
git commit -m "feat(chassis): implement the mode state machine"
git push
```

---

## 自查

```bash
python tools/grade.py cpp3 .
```

**期望看到：**

```text
┌────────────────────────────────────────────────────────────┐
│ C++03 · 枚举、switch 与指针                                │
├────────────────────────────────────────────────────────────┤
│ ✅ 能构建                 cmake 配置 + 编译通过            │
│ ✅ test_chassis 全过      chassis 7/7                      │
│ ✅ test_motor 没被改坏    motor 12/12                      │
│ ✅ message 格式           1/1 条合规                       │
├────────────────────────────────────────────────────────────┤
│ 结论   PASS                                                │
└────────────────────────────────────────────────────────────┘
```

> 第二、三条都是"测试全过"，但查的是不同的测试：一个是你这次写的，
> 一个是上次写的。**改坏前面的东西，这里会当场发现。**

---

## 提交

把自查输出截图发到飞书群。

---

## 评分

**只有 PASS / FAIL。**

- [ ] 能构建
- [ ] `test_chassis` 全部用例通过
- [ ] `tests/` 下的测试文件**没有被修改**
- [ ] 历史里有**你自己写的提交**
- [ ] `test_motor` 仍然全过（没把 `cpp2` 的成果改坏）
- [ ] commit message 符合 `type(scope): subject`
- [ ] commit message 不是废话（`update` / `修改` 这类不合格）

---

## 常见错误

| 症状 | 原因 | 怎么办 |
| --- | --- | --- |
| 编译警告说 `kCalibrate` 没处理 | `switch` 漏了 `case` | 四个都要写全 |
| 返回了 `"?"` | 新值走进了兜底分支 | 检查 `case` 的写法 |
| `modeName(kIdle)` 得到 `"?"` | `switch` 里漏了 `kIdle` | 同上 |
| 编译报"函数可能没有返回值" | 少了 `switch` 后面的兜底 `return` | 加一行 `return "?";` |
| `follow: 0.5 truncates to 0` 挂了 | 把 `0.5` 当成了 `1` | 浮点转整数是截断，`0.5` → `0` |
| `test_motor` 挂了 | 动过 `motor.cpp` | 那是 `cpp2` 的成果，别改；`git checkout` 回来 |
| 段错误 | 用 `wheels_[i]` 时越界 | 循环条件是 `i < wheel_count_`，不是硬编码 4 |

---

## 参考

| 内容 | 在哪 |
| --- | --- |
| 枚举与 `enum class` | 讲义 §8.1、§8.2 |
| `switch` 覆盖枚举、为什么不写 `default` | 讲义 **§8.3** |
| 指针、指针数组、指针的指针 | 讲义 **§6b** |
| 真实仓库的 `Mode_e` / `ClampState` | 讲义 §8.5 |

---

## 做完之后

最后一份 `cpp4` 讲位运算：把一个 `int16` 拆成两个字节、再拼回来。
那是查 CAN 报文的基本功，也是 Day 3 CAN 课的前置。
