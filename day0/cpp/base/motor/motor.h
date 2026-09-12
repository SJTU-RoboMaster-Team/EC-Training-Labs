#ifndef CPP_LAB_BASE_MOTOR_MOTOR_H
#define CPP_LAB_BASE_MOTOR_MOTOR_H

#include <cstdint>

#include "base/motor/dji_motor_driver.h"

// 电机对象。
//
// 抽象自真实仓库 wheel-legged/base/motor/motor.h + .cpp。
// 真实那一份的构造函数参数比这里多得多（PID、卡尔曼参数、函数指针……），
// 这里只留下讲得清、而且你真的会用到的那部分。

namespace motor {

enum class Type : uint8_t {
  M3508 = 0,   // 控制量 [-16384, 16384]
  M2006 = 1,   // 控制量 [-10000, 10000]
  GM6020 = 2,  // 控制量 [-30000, 30000]
};

// 控制量上限由型号决定。
// 真实仓库里是 `motor->info_.type` 上面的一个 switch（motor.cpp:31 附近）。
int16_t intensityLimit(Type type);

class Motor {
 public:
  Motor(djimotor::RawData raw, Type type);

  void update(djimotor::RawData raw);

  // 设定目标转矩，返回这次实际发出的控制量（已经限幅并转成整数）。
  //
  // ⚠️ TODO(cpp2)：实现它。要点：
  //   ① 先把目标值限幅到 [-intensityLimit(type_), +intensityLimit(type_)]
  //   ② **限幅之后**再做浮点→整数的转换。
  //      先转再限幅会怎样？想一想 target_torque = 1e6 的时候。
  //   ③ 转换用 static_cast<int16_t>(...)，不要用 C 风格强转
  //   ④ 把结果存进 intensity_ 并返回，让 intensity() 反映最后一次的结果
  //
  //   这一节的重点是**函数参数和类型转换**，不是算法。
  int16_t setTorque(float target_torque);

  int16_t intensity() const { return intensity_; }
  const djimotor::RawData& raw() const { return raw_; }
  Type type() const { return type_; }

 private:
  djimotor::RawData raw_;
  Type type_;
  int16_t intensity_ = 0;
};

}  // namespace motor

#endif  // CPP_LAB_BASE_MOTOR_MOTOR_H
