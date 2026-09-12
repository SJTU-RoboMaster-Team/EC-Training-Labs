#ifndef CPP_LAB_BASE_MOTOR_MOTOR_H
#define CPP_LAB_BASE_MOTOR_MOTOR_H

#include <cstdint>

#include "base/motor/dji_motor_driver.h"

// 电机对象。
//
// 抽象自真实仓库：
//   wheel-legged/base/motor/motor.h:60    Motor(...) 构造函数
//   wheel-legged/base/motor/motor.h:183   float (*model_)(...)
//   wheel-legged/base/motor/motor.cpp:153 if (model_ != nullptr) { ... }

namespace motor {

enum class Type : uint8_t {
  M3508 = 0,   // 控制量 [-16384, 16384]
  M2006 = 1,   // 控制量 [-10000, 10000]
  GM6020 = 2,  // 控制量 [-30000, 30000]
};

// 控制量上限由型号决定
int16_t intensityLimit(Type type);

// 前馈模型：给定目标转矩和当前转速，算出应该给多少控制量。
//
// **这是一个函数指针类型**。真实仓库里它长这样（motor.h:70）：
//     float (*model)(const Motor&, const float&, const float&) = nullptr
// `= nullptr` 表示"这个电机没接前馈模型"，**调用前必须先判空**。
using ModelFn = float (*)(float target_torque, float speed);

class Motor {
 public:
  Motor(djimotor::RawData raw, Type type, ModelFn model = nullptr);

  void update(djimotor::RawData raw);

  // 设定目标转矩，返回这次实际发出的控制量。
  //
  // ⚠️ TODO(cpp4)：实现它。要点：
  //   ① model_ 可能是 nullptr（构造时没给模型），**调用前必须判空**
  //   ② 有模型就用模型算，没有就直接用目标转矩
  //   ③ 最后按型号限幅，并把结果存进 intensity_
  //
  //   真实代码就是这么写的（motor.cpp:153）：
  //       if (model_ != nullptr) {
  //         intensity_ = model_(*this, control_data_.target_torque, ...);
  //       }
  int16_t setTorque(float target_torque);

  int16_t intensity() const { return intensity_; }
  const djimotor::RawData& raw() const { return raw_; }
  Type type() const { return type_; }

 private:
  djimotor::RawData raw_;
  Type type_;
  int16_t intensity_ = 0;
  ModelFn model_;      // ← 函数指针成员；nullptr 表示"没接模型"
};

}  // namespace motor

#endif  // CPP_LAB_BASE_MOTOR_MOTOR_H
