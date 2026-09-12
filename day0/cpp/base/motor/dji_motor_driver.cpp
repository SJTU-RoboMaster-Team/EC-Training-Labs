#include "base/motor/dji_motor_driver.h"

namespace djimotor {

RawData parseRawData(const uint8_t data[8]) {
  RawData out;
  // TODO(cpp5)：按上面的协议解开这 8 个字节。
  (void)data;
  return out;
}

void packControl(const int16_t intensity[4], uint8_t out[8]) {
  // TODO(cpp5)：把 4 个 int16 拆成 8 个字节，高字节在前。
  (void)intensity;
  for (int i = 0; i < 8; ++i) {
    out[i] = 0;
  }
}

}  // namespace djimotor
