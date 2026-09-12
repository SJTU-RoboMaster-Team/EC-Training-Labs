#include "base/common/math.h"
#include "tests/test_util.h"

int main() {
  using namespace test;

  // limit：普通限幅
  eq_f(math::limit(5.0f, 0.0f, 3.0f), 3.0f, "limit above max");
  eq_f(math::limit(-5.0f, 0.0f, 3.0f), 0.0f, "limit below min");
  eq_f(math::limit(1.5f, 0.0f, 3.0f), 1.5f, "limit inside");

  // loopLimit：折到 [min, max)
  eq_f(math::loopLimit(190.0f, -180.0f, 180.0f), -170.0f, "loopLimit over max");
  eq_f(math::loopLimit(-190.0f, -180.0f, 180.0f), 170.0f, "loopLimit under min");
  eq_f(math::loopLimit(10.0f, -180.0f, 180.0f), 10.0f, "loopLimit inside");
  // 折好几圈也要对 —— 用 while 而不是 if 才做得到
  eq_f(math::loopLimit(730.0f, -180.0f, 180.0f), 10.0f, "loopLimit two turns");

  // degNormalize180：跨零那一圈（和 HW2 的 test_encoder 同一个概念）
  eq_f(math::degNormalize180(350.0f), -10.0f, "degNormalize180 350 -> -10");
  eq_f(math::degNormalize180(-350.0f), 10.0f, "degNormalize180 -350 -> 10");
  eq_f(math::degNormalize180(12.0f), 12.0f, "degNormalize180 inside");

  // isNanOrInf：位级检查
  float nan_v = 0.0f;
  float inf_v = 1.0f;
  {
    uint32_t bits = 0x7FC00000u;   // quiet NaN
    __builtin_memcpy(&nan_v, &bits, 4);
    bits = 0x7F800000u;            // +inf
    __builtin_memcpy(&inf_v, &bits, 4);
  }
  float one = 1.0f;
  ok(math::isNanOrInf(&nan_v), "isNanOrInf(NaN)");
  ok(math::isNanOrInf(&inf_v), "isNanOrInf(inf)");
  ok(!math::isNanOrInf(&one), "isNanOrInf(1.0) is false");

  return report("test_math");
}
