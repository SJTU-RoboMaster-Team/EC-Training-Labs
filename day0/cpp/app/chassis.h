#ifndef CPP_LAB_APP_CHASSIS_H
#define CPP_LAB_APP_CHASSIS_H

#include <cstdint>

#include "base/motor/motor.h"

// 一个简化过的底盘控制状态机。
//
// 抽象自真实仓库的分层：
//   wheel-legged/app/wheel_legged_chassis.h
//   dual-arm/MasterArm/app/arm.h:176   （ArmCore 的纯虚接口；这一份没用虚函数）

namespace app {

// 底盘工作模式 —— 真实仓库里叫 Mode_e（app/arm.h）。
// 注意真实仓库写的是 `enum Mode_e : uint8_t { ... }`（不带 class），
// 因为它要和 C 代码共用一个字节。
enum class Mode : uint8_t {
  kIdle = 0,
  kSpin,       // 小陀螺
  kFollow,     // 跟随
  kCalibrate,  // 标定
};

// 模式名 —— 调试输出用。
//
// ⚠️ TODO(cpp3)：实现它。
//   要求：**覆盖 Mode 的每一个值**，并且不要把最后一个 case 写成 default。
//   为什么：这样以后有人往 Mode 里加了新值，编译器会在**这里**报警告，
//   而不是让新值悄悄走到兜底分支上。
const char* modeName(Mode m);

class Chassis {
 public:
  Chassis(motor::Motor* wheels, int wheel_count, Mode mode = Mode::kIdle);

  // 每个控制周期调一次。
  // 返回这一周期四个轮子控制量的**和**（用来判断"到底有没有输出"）。
  //
  // ⚠️ TODO(cpp3)：实现它。规则：
  //   kIdle      → 所有轮子 torque = 0
  //   kSpin      → 所有轮子 torque = spin_torque_
  //   kFollow    → 所有轮子 torque = follow_torque_
  //   kCalibrate → 所有轮子 torque = 0，而且**不能因为"堵转"中断**
  //                （标定时轮子会顶到限位，那不是堵转）
  int32_t update();

  void setMode(Mode m) { mode_ = m; }
  Mode mode() const { return mode_; }
  int wheelCount() const { return wheel_count_; }

 private:
  motor::Motor* wheels_;      // ← 指针 + 数组长度，战队代码里最常见的写法
  int wheel_count_;
  Mode mode_;
  float spin_torque_ = 1.0f;
  float follow_torque_ = 0.5f;
};

}  // namespace app

#endif  // CPP_LAB_APP_CHASSIS_H
