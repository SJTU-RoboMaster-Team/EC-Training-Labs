#include "app/chassis.h"

namespace app {

const char* modeName(Mode m) {
  // TODO(cpp3)
  (void)m;
  return "?";
}

Chassis::Chassis(motor::Motor* wheels, int wheel_count, Mode mode)
    : wheels_(wheels), wheel_count_(wheel_count), mode_(mode) {
  // 想一想：如果 wheels 是 nullptr、或者 wheel_count 是负数，这里该怎么做？
  // 真实仓库通常是直接信任调用方 —— 先想清楚这个假设什么时候会不成立。
}

int32_t Chassis::update() {
  // TODO(cpp3)
  return 0;
}

}  // namespace app
