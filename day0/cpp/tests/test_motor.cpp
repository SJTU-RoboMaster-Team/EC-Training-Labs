#include "base/motor/motor.h"
#include "tests/test_util.h"

int main() {
  using namespace test;

  eq_i(motor::intensityLimit(motor::Type::M3508), 16384, "limit M3508");
  eq_i(motor::intensityLimit(motor::Type::M2006), 10000, "limit M2006");
  eq_i(motor::intensityLimit(motor::Type::GM6020), 30000, "limit GM6020");

  djimotor::RawData raw;

  // ① 正常范围：直接通过
  {
    motor::Motor m(raw, motor::Type::M3508);
    eq_i(m.setTorque(10.0f), 10, "small torque passes through");
    eq_i(m.setTorque(-500.0f), -500, "negative torque");
  }

  // ② 浮点转整数是**截断**，不是四舍五入
  {
    motor::Motor m(raw, motor::Type::M3508);
    eq_i(m.setTorque(1.9f), 1, "truncates toward zero (1.9 -> 1)");
    eq_i(m.setTorque(-1.9f), -1, "truncates toward zero (-1.9 -> -1)");
  }

  // ③ 限幅：M2006 上限 10000
  {
    motor::Motor m(raw, motor::Type::M2006);
    eq_i(m.setTorque(20000.0f), 10000, "clamp to M2006 limit");
    eq_i(m.setTorque(-20000.0f), -10000, "clamp negative side too");
  }

  // ④ 超大值：先限幅再转换才不会出事。
  //    如果先 static_cast<int16_t>(1e9f) 再限幅，结果完全不可预期。
  {
    motor::Motor m(raw, motor::Type::M3508);
    eq_i(m.setTorque(1.0e9f), 16384, "1e9 clamps to M3508 limit");
    eq_i(m.setTorque(-1.0e9f), -16384, "negative 1e9 clamps too");
  }

  // ⑤ intensity() 反映最后一次结果
  {
    motor::Motor m(raw, motor::Type::M3508);
    m.setTorque(500.0f);
    eq_i(m.intensity(), 500, "intensity() keeps last value");
    eq_i(m.setTorque(0.0f), 0, "zero torque");
  }

  return report("test_motor");
}
