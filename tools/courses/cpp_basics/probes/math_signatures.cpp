// 契约探针：`math` 命名空间里四个函数的签名必须是这样。
//
// 探针**不写进学生仓库** —— grader 把它和学生的头文件一起编译，
// 编译过了就说明签名对。报错信息就是编译器自己说的话。
//
// 为什么四个都查：原来只查了 `loopLimit` 一个，于是把
// `limit(float,float,float)` 改成 `(double,double,double)`、
// 或者把 `degNormalize180` 的返回类型改成 `double`，都能蒙过去。
// 而任务书上写的是「函数签名没改」—— 说的是四个。
// （这是学生视角走查时发现的：文档的承诺比检查的范围大。）
//
// 签名出处：wheel-legged/base/common/math.h
//   float limit(float val, float min, float max);
//   float loopLimit(float val, const float& min, const float& max);
//   float degNormalize180(float angle);
//   bool  isNanOrInf(const float* ptr);
// 注意 limit 全按值传、loopLimit 后两个按 const 引用传、isNanOrInf 收指针 ——
// 真实代码就是三种写法混着的。
#include <type_traits>

#include "base/common/math.h"

static_assert(std::is_same_v<decltype(&math::limit), float (*)(float, float, float)>,
              "math::limit 的签名是 float limit(float val, float min, float max) —— 三个都按值传");

static_assert(
    std::is_same_v<decltype(&math::loopLimit),
                   float (*)(float, const float&, const float&)>,
    "math::loopLimit 的签名是 float loopLimit(float val, const float& min, "
    "const float& max) —— 第一个按值，后两个按 const 引用");

static_assert(std::is_same_v<decltype(&math::degNormalize180), float (*)(float)>,
              "math::degNormalize180 的签名是 float degNormalize180(float angle) —— "
              "参数和返回都是 float，不能改成 double（两个工程都是单精度 FPU）");

static_assert(std::is_same_v<decltype(&math::isNanOrInf), bool (*)(const float*)>,
              "math::isNanOrInf 的签名是 bool isNanOrInf(const float* ptr) —— "
              "收的是指针，不是引用、不是 float");
