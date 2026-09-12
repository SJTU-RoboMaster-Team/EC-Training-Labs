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

Motor::Motor(djimotor::RawData raw, Type type) : raw_(raw), type_(type) {}

void Motor::update(djimotor::RawData raw) { raw_ = raw; }

int16_t Motor::setTorque(float target_torque) {
  // TODO(cpp2)：见头文件里的说明。
  //
  // 提示：限幅这一步，真实仓库是这么做的（math.cpp 里的 math::limit）：
  //     float limit(float val, float min, float max);
  // 你可以直接调它 —— 那个函数在 cpp1 里你要自己实现。
  (void)target_torque;
  intensity_ = 0;
  return intensity_;
}

}  // namespace motor
