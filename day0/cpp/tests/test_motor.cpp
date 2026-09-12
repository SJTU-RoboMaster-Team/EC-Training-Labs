#include "base/motor/motor.h"
#include "tests/test_util.h"

// 一个假的前馈模型：控制量 = 目标转矩 * 100 + 转速
static float fakeModel(float target_torque, float speed) {
  return target_torque * 100.0f + speed;
}

int main() {
  using namespace test;

  eq_i(motor::intensityLimit(motor::Type::M3508), 16384, "limit M3508");
  eq_i(motor::intensityLimit(motor::Type::M2006), 10000, "limit M2006");
  eq_i(motor::intensityLimit(motor::Type::GM6020), 30000, "limit GM6020");

  djimotor::RawData raw;

  // ① 没接模型（model = nullptr）—— 这是最容易崩的地方
  {
    motor::Motor m(raw, motor::Type::M3508, nullptr);
    eq_i(m.setTorque(10.0f), 10, "no model: torque passes through");
  }

  // ② 接了模型
  {
    motor::Motor m(raw, motor::Type::M3508, &fakeModel);
    eq_i(m.setTorque(10.0f), 1000, "with model: 10*100+0");
  }

  // ③ 限幅：M2006 上限 10000
  {
    motor::Motor m(raw, motor::Type::M2006, nullptr);
    eq_i(m.setTorque(20000.0f), 10000, "clamp to M2006 limit");
    eq_i(m.setTorque(-20000.0f), -10000, "clamp negative side too");
  }

  // ④ intensity() 反映最后一次的结果
  {
    motor::Motor m(raw, motor::Type::M3508, nullptr);
    m.setTorque(500.0f);
    eq_i(m.intensity(), 500, "intensity() keeps last value");
  }

  return report("test_motor");
}
