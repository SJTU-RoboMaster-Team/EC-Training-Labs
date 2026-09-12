# HW3 · 编译与链接

前两份作业你都在改**逻辑**。这一份换个角度：看**代码是怎么变成可执行文件的**。

你会故意制造一个链接错误，看懂它，再修好它。

---

## 学习目标

1. 分清**编译**和**链接**是两个阶段，各自在做什么
2. 看见 `undefined reference to ...` 时，知道它在说什么、去哪找问题
3. 知道"声明"和"定义"的区别，以及为什么缺定义编译能过、链接会挂
4. 把这件事**写下来**——能说清楚才算真的懂

---

## 开始之前

- [ ] 完成了 HW2：`python tools/build.py` 全绿（`encoder 4/4 · clamp 4/4`）
- [ ] 完成了 HW2 的提交，`git status` 干净
- [ ] 看过了录播 `Tools/01-keil-stm32.md`（讲编译流程的那一段）

---

## 获取代码

```bash
cd EC-Training-Labs/day0/project
git switch main
git pull
```

> ⚠️ **工作目录：后面所有命令都在 `day0/project/` 里执行。**

---

## 任务

这一份**故意分两步**：先弄坏，再修好。别跳过第一步。

### Task 1 · 把逻辑从「头文件里的实现」改成「声明 + 独立实现」

HW2 里你修好的那段归一化逻辑，现在是**直接写在 `base/math.h` 里的**：

```cpp
inline float deg_normalize_180(float d) {
  if (d > 180.0f) {
    d -= 360.0f;
  } else if (d < -180.0f) {
    d += 360.0f;
  }
  return d;
}
```

**现在把它挪出去，做成一个正经的函数。** 这是真实项目里最常见的重构动作。

**第一步：把 `base/math.h` 里这个函数整个删掉，换成一行声明：**

```cpp
// 把角度折算到 [-180, 180)
float wrap_angle_deg(float deg);
```

**第二步：打开 `app/motor_monitor.cpp`，把调用点改成新名字：**

```cpp
// 改前
data_.angle += deg_normalize_180(raw_angle_deg - data_.last_raw_angle);

// 改后
data_.angle += wrap_angle_deg(raw_angle_deg - data_.last_raw_angle);
```

**现在先不要写实现。**

---

### Task 2 · 构建，观察报错

```bash
python tools/build.py
```

**你应该看到构建失败**，错误信息里有类似这样的行：

```text
app/motor_monitor.cpp:17: undefined reference to `wrap_angle_deg(float)'
collect2: error: ld returned 1 exit status
```

**怎么验证：** 把这条报错**完整读一遍**，回答：

- [ ] 报错里出现了 `undefined reference` 还是 `error: expected ...`？
- [ ] 结尾是 `ld returned 1` 还是 `compilation terminated`？
- [ ] 报错指出的文件是 `motor_monitor.cpp` 还是编译器在说别的？

> 💡 **这两个词的区别就是这份作业的全部内容：**
> `undefined reference` 是**链接器**（ld）在说"我知道有这个函数，但找不到它的实现"。
> `error: expected ...` 才是**编译器**在说"你这段代码语法/类型不对"。

> ⚠️ **看不到这条报错？** 先确认你确实改了 `motor_monitor.cpp` 的调用点——
> 只删 `math.h` 里的实现、没改调用点的话，报的会是 `deg_normalize_180` 找不到，
> 道理一样，也说明你完成了这份作业。

---

### Task 3 · 想清楚一个问题

**为什么编译 `motor_monitor.cpp` 的时候不报错？**

`math.h` 里明明只有一个声明、没有实现，编译器为什么放它过去？

<details>
<summary>想不出来？点开看提示（只说思路）</summary>

想一下：编译器处理 `motor_monitor.cpp` 的时候，**它看不看得到别的 .cpp 文件？**

如果看不到，那它凭什么判断"这个函数在别处有没有实现"？

那这个判断是谁来做的？它在什么时候做？它需要看什么？
</details>

---

### Task 4 · 修好它

给 `wrap_angle_deg` 补上**实现**。两种做法都行，选一种：

#### 做法 A · 新建一个 .cpp（推荐，更接近真实工程）

1. 新建 `base/angle.cpp`：

   ```cpp
   #include "base/math.h"

   float wrap_angle_deg(float deg) {
     while (deg >= 180.0f) deg -= 360.0f;
     while (deg < -180.0f) deg += 360.0f;
     return deg;
   }
   ```

2. **把它加进 `CMakeLists.txt`**：

   ```cmake
   add_library(day0_core
     app/control.cpp
     app/motor_monitor.cpp
     app/clamp.cpp
     base/angle.cpp        # ← 加这一行
   )
   ```

#### 做法 B · 留在头文件里

在 `base/math.h` 里把声明直接写成 `inline` 定义：

```cpp
inline float wrap_angle_deg(float deg) {
  while (deg >= 180.0f) deg -= 360.0f;
  while (deg < -180.0f) deg += 360.0f;
  return deg;
}
```

**怎么验证：**

```bash
python tools/build.py
```

- [ ] 构建成功
- [ ] `test_encoder` 和 `test_clamp` **全部通过**
      （你只是把逻辑换了个地方，行为不该变）

> ⚠️ **做做法 A 的时候，如果你忘了改 `CMakeLists.txt`，会看到一模一样的链接错误。**
> 这就是链接错误最常见的真实原因：**文件写了，但没加进构建系统**。

---

### Task 5 · 把你想清楚的写下来

在 `day0/homework/answers-hw3.md` 新建一个文件，回答三个问题。
**不用写长，每问两三句就行，但要写人话，不要抄。**

```markdown
# HW3 · 我的回答

## 1. 编译阶段和链接阶段分别在做什么？

（提示：一个在检查单个文件"写对没有"，一个在把多个文件"拼起来"。
  说清各自输入什么、输出什么。）

## 2. `undefined reference` 是哪一个阶段的错误？为什么编译 control.cpp 时不报？

（提示：想想编译器能不能看到别的 .cpp。）

## 3. 你最后是怎么修的？为什么那样能解决？

（写你实际用的做法：新建 .cpp 加进 CMakeLists，还是改成 inline。）
```

---

### Task 6 · 提交

```bash
git status
git diff                     # 看一遍
git add app/arm.h app/control.cpp base/angle.cpp CMakeLists.txt
git add ../homework/answers-hw3.md
git diff --staged
git commit
```

> 如果你把 `arm.h` 的声明和 `control.cpp` 的调用、以及新文件的实现
> 分散在几个 commit 里也没问题——**只要每个 commit 的 message 说得清**。

commit message 参考：

```text
feat(arm): add wrap_angle_deg and wire it into the control loop
```

**怎么验证：** `git log --oneline -3` 能看到你的提交。

---

## 自查

```bash
# 在你仓库的根目录下（就是 EC-Training-Labs/ 这一层）
python tools/grade.py hw3 .
```

> **`grade.py` 就在你的仓库里**（`tools/grade.py`）。它和老师用的是同一份代码，
> 所以**你跑出什么结果，老师就验收什么结果**。

**期望看到：**

```text
┌────────────────────────────────────────────────────────────┐
│ HW3 · 编译与链接                                           │
├────────────────────────────────────────────────────────────┤
│ ✅ 能构建                 cmake 配置 + 编译通过            │
│ ✅ 测试全部通过           clamp 4/4 · encoder 4/4          │
│ ✅ 回答了三个问题         answers-hw3.md 共 NNN 字         │
│ ✅ 新函数确实实现了       wrap_angle_deg 有定义            │
├────────────────────────────────────────────────────────────┤
│ 结论   PASS                                                │
└────────────────────────────────────────────────────────────┘
```

---

## 提交

把**那个链接错误的截图**和**自查输出的截图**一起发到飞书群。

> 链接错误的截图很重要——那是这份作业的"证据"。
> 如果忘了截，可以 `git stash` 掉修复、重新构建一次再截，然后 `git stash pop` 回来。

---

## 评分

**只有 PASS / FAIL。**

- [ ] 工程能编译通过（说明链接错误已经修好）
- [ ] `test_encoder` 与 `test_clamp` **全部通过**
- [ ] `day0/homework/answers-hw3.md` 存在，且三个问题都有实质回答
- [ ] `wrap_angle_deg` 确实有实现（不是只有声明）

---

## 常见错误

| 症状 | 原因 | 怎么办 |
| --- | --- | --- |
| 加了实现还是 `undefined reference` | 做法 A 忘了改 `CMakeLists.txt` | 把 `base/angle.cpp` 加进 `add_library` |
| 报的是 `error: expected ';'` 之类 | 那是**编译**错误，不是链接错误 | 检查语法/括号/分号 |
| `wrap_angle_deg` 重定义 | 头文件里写了 `inline`，.cpp 里又定义了一次 | 两种做法**只选一种** |
| 报的是 `deg_normalize_180` 找不到 | 只删了实现、没改调用点 | 一样是链接错误，改完调用点即可 |
| 构建成功但 `test_clamp` 挂了 | 改坏了别的东西 | `git diff` 看看你是不是动了 clamp 相关代码 |
| 忘记截链接错误的图 | —— | `git stash` → 构建报错 → 截图 → `git stash pop` |

---

## 参考

| 内容 | 在哪 |
| --- | --- |
| 编译 / 链接流程 | Day 0 录播 · `Tools/01-keil-stm32.md` |
| CLion 里怎么看构建输出 | Day 0 录播 · `Tools/02-clion-setup.md` |
| CMakeLists 是什么 | 同上 |

---

## 做完之后

以后你在真实仓库里看到 `undefined reference`，第一反应应该是：
**"这个符号定义了没有？定义了的话，那个文件加进构建了吗？"**

这比背一百条编译错误都有用。

下一份作业（HW4）会离开"代码对不对"，去看"代码排得整不整齐"。
