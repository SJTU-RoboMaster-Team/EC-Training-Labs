// 契约探针：`Motor::setTorque` 的签名必须是这样。
//
// 探针**不写进学生仓库** —— grader 把它和学生的头文件一起编译，
// 编译过了就说明签名对。报错信息就是编译器自己说的话。
//
// 要求三件事：
//   · 参数是**按值传的 float**（不是 double，也不是 const float&）
//   · 返回类型是 int16_t
//   · 是普通成员函数（不是 static）
//
// 为什么参数按值传：`float` 只有 4 字节，传引用反而多一次内存访问。
// 真实仓库 wheel-legged/base/common/math.h 里 `limit` 也是全按值传的。
#include <type_traits>

#include "base/motor/motor.h"

static_assert(
    std::is_same_v<decltype(&motor::Motor::setTorque), int16_t (motor::Motor::*)(float)>,
    "motor::Motor::setTorque 必须是 int16_t setTorque(float) —— "
    "参数按值传 float（4 字节，传引用更慢），返回 int16_t");
