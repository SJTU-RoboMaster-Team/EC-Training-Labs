// 契约探针：浮点一律用 float，不许出现 double。
//
// 为什么这不是"风格偏好"：两个真实工程都只开单精度 FPU
//   wheel-legged/mcu/stm32f407/CMakeLists.txt   -mfpu=fpv4-sp-d16
//   dual-arm/MasterArm/mcu/stm32h723/...        -mfpu=fpv5-sp-d16
// double 会退化成软件模拟，一次除法就是几十条指令。
//
// 实测：战队自己的 70822 行代码里 float 出现 5233 次，double 0 次。
#include <type_traits>

#include "base/common/math.h"

static_assert(std::is_same_v<decltype(math::degNormalize180(0.0f)), float>,
              "math::degNormalize180 必须返回 float —— 两个工程都是单精度 FPU，"
              "double 是软件模拟");
