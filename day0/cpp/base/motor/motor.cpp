#include "base/motor/motor.h"

namespace motor {

int16_t intensityLimit(Type type) {
  switch (type) {
    case Type::M3508:
      return 16384;
    case Type::M2006:
      return 10000;
    case Type::GM6020:
      return 30000;
  }
  return 0;
}

Motor::Motor(djimotor::RawData raw, Type type, ModelFn model)
    : raw_(raw), type_(type), model_(model) {}

void Motor::update(djimotor::RawData raw) { raw_ = raw; }

int16_t Motor::setTorque(float target_torque) {
  // TODO(cpp2)：见头文件里的说明。
  //   提示：算出来的结果可能是 float，转成 int16_t 之前先想清楚
  //   「直接强转」和「先限幅再转」有什么区别。
  (void)target_torque;
  intensity_ = 0;
  return intensity_;
}

}  // namespace motor
