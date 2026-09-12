# cpp1 · 声明与定义

> **这是 C++ 线的第一份练习**（`cpp1`–`cpp4`）。它和 `HW1`–`HW5` 是两条独立的线，
> 工程也不一样：这份在 [`../cpp/`](../cpp/) 里。

你打开工程第一眼就会撞上一条报错。这份练习要做的事情就是搞懂它、然后修掉它。

---

## 学习目标

1. 分清**声明**和**定义**，知道各自的活是谁干的（编译器还是链接器）
2. 看懂 `undefined reference` 这条报错，知道该去哪里找问题
3. 知道"文件写了"和"加进构建系统"是两件事

---

## 开始之前

- [ ] 读过讲义 [`../cpp/lecture.md`](../cpp/lecture.md) 的 **§3**（声明与定义）和 **§4**（`inline`）
- [ ] 讲义 **§6.7**（真实仓库里 `loopLimit` 的原文）也扫过一眼
- [ ] 讲义 **§6c.1–§6c.4**（位运算、类型转换、整型提升）——
      `isNanOrInf` 那个函数要用它看 IEEE754 的位
- [ ] 电脑上有 cmake 和 C++ 编译器（`g++` 或 MinGW）

> 没读讲义直接做也行，但 §3.5 讲的就是你马上要看到的那条报错。

---

## 获取代码

工程就在你 fork 的仓库里，不用另外下载：

```bash
cd EC-Training-Labs/day0/cpp
```

> ⚠️ **后面所有命令都在 `day0/cpp/` 里执行**，自查那一步要回到仓库根目录。

---

## 背景：这个工程一开始是编不过的

先构建一次看看：

```bash
cmake -S . -B build
cmake --build build
```

> **如果 cmake 配置就失败了**，多半是生成器没选对（Windows 上最常见）。
> 换一条试：
>
> ```bash
> cmake -S . -B build -G Ninja                  # 装了 Ninja
> cmake -S . -B build -G "MinGW Makefiles"      # 装了 MinGW
> ```
>
> 换生成器要**先把 `build/` 删掉**，否则会报
> `generator does not match the generator used previously`。
> 详⻅ `../notes/02-clion-setup.md` §2。

**它一定会失败。** 报错长这样：

```text
[ 38%] Built target cpp_lab_core
tests/test_math.cpp:8: undefined reference to `math::limit(float, float, float)'
collect2: error: ld returned 1 exit status
```

这不是你的环境坏了，是**故意留的**。

`base/common/math.cpp` 现在是个空文件，只有一行注释。`base/common/math.h` 里
声明了四个函数，但没有任何一个 `.o` 里有它们的定义。

> **为什么编译能过、链接才报？**
> 编译 `test_math.cpp` 时，编译器只看到头文件里的声明 —— "有这么个函数，参数是
> 三个 `float`，返回 `float`"。语法和类型都对，它就放行。至于这个函数在别处
> 有没有实现，编译器**看不到别的 `.cpp`**，也管不着。那是链接器的活。
>
> 讲义 §3.5 有完整的拆解。

---

## 任务

### Task 1 · 先把报错读明白

**先别改代码。** 对着上面那条报错回答三个问题：

- [ ] 这是**编译**错误还是**链接**错误？
- [ ] 报错里指的 `tests/test_math.cpp:8` 是"缺定义的地方"吗？
- [ ] 链接器在找的那个东西，为什么找不到？

答不出来就回讲义 §3.5。**这一步不能跳** —— 你以后每周都会看到这条报错。

### Task 2 · 看看头文件里声明了什么

打开 `base/common/math.h`，四个函数：

```cpp
float limit(float val, float min, float max);
float loopLimit(float val, const float& min, const float& max);
float degNormalize180(float angle);
bool  isNanOrInf(const float* ptr);
```

注意每一行的**参数写法不一样**，这是照抄真实仓库的：

- `limit` 三个参数全按值传
- `loopLimit` 后两个按 `const` 引用传
- `isNanOrInf` 收的是**指针**

**别改这些签名。** 验收会拿一小段 `static_assert` 和你的头文件一起编译，
签名变了就编译不过 —— 那时你会看到一条写给人的报错。

### Task 3 · 在 `math.cpp` 里把定义写出来

四个函数都要写。提示（不给答案）：

**`limit`** —— 普通限幅：比 `max` 大就返回 `max`，比 `min` 小就返回 `min`，否则原样返回。

**`loopLimit`** —— 把它折算到 `[min, max)` 区间。
提示：**用 `while` 不要用 `if`**。测试里有一条 `loopLimit(730, -180, 180)` 要求得 10
（转了两圈），一个 `if` 处理不了。
边界情况：`min >= max` 时直接返回原值。

**`degNormalize180`** —— 一行就够，调 `loopLimit` 把区间设成 `[-180, 180]`。
真实仓库里就是这么写的（讲义 §6.7 有原文）。

**`isNanOrInf`** —— 参数是指针，要先解引用拿到 `float`，再按位看它的指数部分。
IEEE754 的 `float` 里，第 23~30 位是指数；指数全 1（`0xFF`）就说明是 `NaN` 或 `∞`。
提示：拿位的时候别用 `*((uint32_t*)ptr)`（那是未定义行为），用 `__builtin_memcpy`
或 `memcpy` 拷到 `uint32_t` 里。

### Task 4 · 重新构建，跑测试

```bash
cmake --build build
ctest --test-dir build --output-on-failure
```

**期望：** `test_math` 13 个用例全过。

如果某个用例挂了，`ctest` 会把失败那行打出来，格式是
`got X want Y` —— 照这个去对是哪个函数写错了。

### Task 5 · 提交

```bash
cd ../..                     # 回仓库根目录
git add day0/cpp/base/common/math.cpp
git commit -m "feat(math): implement limit / loopLimit / degNormalize180 / isNanOrInf"
git push
```

commit message 用 `type(scope): subject` 格式（和 Git 线的要求一样）。

---

## 自查

```bash
# 在你仓库的根目录下
python tools/grade.py cpp1 .
```

> **`grade.py` 就在你仓库里**（`tools/grade.py`），和老师用的是同一份代码 ——
> 你自查看到的结果，就是验收时会看到的结果。**前提是别改它**：
> 验收时老师用的是他那份，跑的还是同一套规则。


**期望看到：**

```text
┌────────────────────────────────────────────────────────────┐
│ C++01 · 声明与定义                                         │
├────────────────────────────────────────────────────────────┤
│ ✅ 能构建                 cmake 配置 + 编译通过            │
│ ✅ test_math 全过         math 13/13                       │
│ ✅ 4 个函数都有实现       limit, loopLimit, degNormalize…  │
│ ✅ 四个函数签名没改       契约成立（探针编译通过）         │
│ ✅ 测试文件未被修改       day0/cpp/tests 下的文件没被改…   │
│ ✅ 你自己有提交           1 次提交                         │
│ ✅ message 格式           1/1 条合规                       │
│ ✅ message 黑名单         没有低信息量 message             │
├────────────────────────────────────────────────────────────┤
│ 结论   PASS                                                │
└────────────────────────────────────────────────────────────┘
```

> 如果只看到一条红、后面几条是灰的「跳过」—— 那是对的。这份练习的检查有先后
> 顺序，第一条没过时后面不跑，免得你看到一片红。

---

## 提交

把 `python tools/grade.py cpp1 .` 的输出截图发到飞书群。

---

## 评分

**只有 PASS / FAIL。** 下面这些必须全部通过：

- [ ] 能构建（cmake 配置 + 编译都成功）
- [ ] `test_math` 13 个用例全过
- [ ] `limit` / `loopLimit` / `degNormalize180` / `isNanOrInf` **四个都有实现**
- [ ] **四个函数的签名都没改**（`limit` 全按值、`loopLimit` 后两个 `const float&`、`isNanOrInf` 收指针）
- [ ] `tests/` 下的测试文件**没有被修改**
- [ ] 历史里有**你自己写的提交**
- [ ] commit message 符合 `type(scope): subject`
- [ ] commit message 不是废话（`update` / `修改` 这类不合格）

---

## 常见错误

| 症状 | 原因 | 怎么办 |
| --- | --- | --- |
| 还是 `undefined reference` | 某个函数没写，或者名字拼错 | 看报错里是哪个符号，回 `math.cpp` 对一遍 |
| `loopLimit(730)` 结果不对 | 用了 `if` 而不是 `while` | 一圈折不完就多折几圈 |
| `isNanOrInf(1.0f)` 返回 `true` | 位取错了 | 先 `>> 23` 再 `& 0xFF`，结果是 `0xFF` 才是 NaN/∞ |
| 编译报窄化警告 | `hi << 8` 的类型是 `int` | 先 `static_cast<uint16_t>` 再移位（讲义 §6c.1） |
| 改了函数签名让它编过 | 走错路了 | 签名是题面，不能改。缺的是**定义**，不是声明 |
| `ctest` 说找不到测试 | 没构建成功 | 先看 `cmake --build build` 的输出 |

---

## 参考

| 内容 | 在哪 |
| --- | --- |
| commit message 怎么写 | [`../cpp/README.md`](../cpp/README.md)「提交约定」 |
| 声明 vs 定义、`undefined reference` 根因 | 讲义 **§3** |
| 真实仓库里的 `loopLimit` / `degNormalize180` | 讲义 **§6.7** |
| 位运算与整型提升 | 讲义 §6c.1、§6c.4 |
| 链接错误怎么读 | 讲义 §11.3 |
| 讲义全文 | [`../cpp/lecture.md`](../cpp/lecture.md) |
| commit message 怎么写 | [`../cpp/README.md`](../cpp/README.md) 的「提交约定」一节 |

---

## 做完之后

你刚才修掉的那条报错，和 Git 线的 **HW3** 是同一个东西 ——
只不过 HW3 那边是你自己把定义从 `.cpp` 挪走制造出来的。

下一份 `cpp2` 讲函数参数怎么传，以及为什么**先限幅再转整数**这个顺序不能反。
