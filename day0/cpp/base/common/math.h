#ifndef CPP_LAB_BASE_COMMON_MATH_H
#define CPP_LAB_BASE_COMMON_MATH_H

#include <cstdint>

// 常用数学工具。
//
// 抽象自战队真实仓库：
//   wheel-legged/base/common/math.h     （函数名、命名空间、注释风格照抄）
//   wheel-legged/base/common/math.cpp
// 原文件有二十多个函数，这里只留下讲得清的那几个。

namespace math {

// ── 限幅 ──────────────────────────────────────────────
// 真实仓库里 limit 按值传参、loopLimit 按 const 引用传参。
// 两种写法都对，但你要能说出区别（见讲义「函数与参数传递」）。

float limit(float val, float min, float max);

// 循环限幅：把角度折算到 [min, max) 里。degNormalize180 就是它配上 [-180, 180]。
//
// 注意参数写法：第一个按值传，后两个按 const 引用传 ——
// 这就是真实仓库里的原样（math.h）。两种写法都对，但你要能说清区别。
float loopLimit(float val, const float& min, const float& max);

// 角度规范化(deg -> [-180, 180])
float degNormalize180(float angle);

// ── 浮点位级检查 ──────────────────────────────────────
// 为什么不直接用 std::isnan：Release 用 -Ofast，它打开了 -ffast-math，
// 其中 -ffinite-math-only 会让编译器**假定不存在 NaN**，
// 于是 std::isnan 会被优化成常量 false。所以只能自己看位。
//
// 真实出处 wheel-legged/base/common/math.cpp:157 ——
//   bool math::isNanOrInf(const float* ptr) {
//     uint32_t val = *((uint32_t*)ptr);
//     uint32_t exponent = (val >> 23) & 0xFF;
//     return exponent == 0xFF;
//   }
//
// 注意参数是**指针**不是引用 —— 这也照抄真实代码。
bool isNanOrInf(const float* ptr);

}  // namespace math

#endif  // CPP_LAB_BASE_COMMON_MATH_H
