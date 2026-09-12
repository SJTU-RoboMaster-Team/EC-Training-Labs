#include "base/motor/dji_motor_driver.h"
#include "tests/test_util.h"

int main() {
  using namespace test;

  // 一帧真实形状的反馈：ecd=0x1234, rpm=-100, current=250, temp=42
  //   大端： [0]=0x12 [1]=0x34 | [2]=0xFF [3]=0x9C | [4]=0x00 [5]=0xFA | [6]=42
  const uint8_t frame[8] = {0x12, 0x34, 0xFF, 0x9C, 0x00, 0xFA, 42, 0x00};
  djimotor::RawData d = djimotor::parseRawData(frame);

  eq_i(d.ecd, 0x1234, "parse ecd (big endian)");
  eq_i(d.rotate_speed_rpm, -100, "parse rpm (signed!)");
  eq_i(d.torq_current, 250, "parse current");
  eq_i(d.temp, 42, "parse temp");

  // 打包：4 个控制量 → 8 字节，高字节在前
  const int16_t intensity[4] = {0x1234, 0x0102, -2, -30000};
  uint8_t out[8] = {0};
  djimotor::packControl(intensity, out);

  eq_i(out[0], 0x12, "pack[0] high byte");
  eq_i(out[1], 0x34, "pack[1] low byte");
  eq_i(out[2], 0x01, "pack[2]");
  eq_i(out[3], 0x02, "pack[3]");
  eq_i(out[4], 0xFF, "pack[4] negative high byte");
  eq_i(out[5], 0xFE, "pack[5] negative low byte");
  eq_i(out[6], 0x8A, "pack[6] -30000 high byte");
  eq_i(out[7], 0xD0, "pack[7] -30000 low byte");

  return report("test_can");
}
