#ifndef DAY0_APP_ARM_H
#define DAY0_APP_ARM_H

#include <cstdint>

// 机械臂工作模式
// 注意：这个枚举是"追加点"——新功能往里加一个值就行了，所以谁都来加。
enum Mode_e : uint8_t {
  FOLD,
  CRUISE,
  TWIST,
  EXCHANGE,
  STORAGE_FRONT,
  STORAGE_BACK,
  // TODO(hw5-c): 标定流程现在借用 FOLD 模式，语义不清。
  //              加一个独立的工作模式 CALIBRATE。
};

// 电机反馈摘要（共享类型：谁需要新字段都往这里加）
struct MotorFeedback {
  float angle = 0.0f;
  float speed = 0.0f;
  float current = 0.0f;
  bool online = false;
};

// 夹爪状态
enum class ClampState : uint8_t {
  kIdle,
  kMoving,
  kBlocked,
  kHolding,
};

#endif  // DAY0_APP_ARM_H
