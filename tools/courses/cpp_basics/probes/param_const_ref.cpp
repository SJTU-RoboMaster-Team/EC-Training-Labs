// 契约探针：函数签名必须是这样。
//
// 探针**不写进学生仓库** —— grader 把它和学生的头文件一起编译，
// 编译过了就说明签名对。报错信息就是编译器自己说的话。
//
// 这一条要求 `math::loopLimit` 的后两个参数是 `const float&`。
//
// 出处 wheel-legged/base/common/math.h：
//   float loopLimit(float val, const float& min, const float& max);
// 第一个参数按值传、后两个按 const 引用传 —— 真实代码就是混着写的。
// 这一条不是为了"必须这么写"，而是让他们**看懂**两种写法的区别。
#include <type_traits>

#include "base/common/math.h"

static_assert(
    std::is_same_v<decltype(&math::loopLimit),
                   float (*)(float, const float&, const float&)>,
    "math::loopLimit 的签名要照抄真实仓库：float loopLimit(float val, "
    "const float& min, const float& max) —— 第一个按值，后两个按 const 引用");
