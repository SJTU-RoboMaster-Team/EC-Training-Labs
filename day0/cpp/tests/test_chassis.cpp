#include <string>

#include "app/chassis.h"
#include "tests/test_util.h"

int main() {
  using namespace test;

  // 模式名要覆盖每一个值
  eq_i(std::string(app::modeName(app::Mode::kIdle)) == "kIdle", 1, "modeName kIdle");
  eq_i(std::string(app::modeName(app::Mode::kSpin)) == "kSpin", 1, "modeName kSpin");
  eq_i(std::string(app::modeName(app::Mode::kFollow)) == "kFollow", 1, "modeName kFollow");
  eq_i(std::string(app::modeName(app::Mode::kCalibrate)) == "kCalibrate", 1,
       "modeName kCalibrate");

  motor::Motor wheels[4] = {
      {djimotor::RawData{}, motor::Type::M3508},
      {djimotor::RawData{}, motor::Type::M3508},
      {djimotor::RawData{}, motor::Type::M3508},
      {djimotor::RawData{}, motor::Type::M3508},
  };
  app::Chassis c(wheels, 4);

  c.setMode(app::Mode::kIdle);
  eq_i(c.update(), 0, "idle: no output");

  // kSpin：四个轮子都出 spin_torque_ = 1.0 → 每个 intensity 1，一共 4
  c.setMode(app::Mode::kSpin);
  eq_i(c.update(), 4, "spin: 4 wheels x 1.0");

  // kFollow：follow_torque_ = 0.5 → 转成 int16 是 0
  c.setMode(app::Mode::kFollow);
  eq_i(c.update(), 0, "follow: 0.5 truncates to 0");

  c.setMode(app::Mode::kCalibrate);
  eq_i(c.update(), 0, "calibrate: no output");

  eq_i(c.wheelCount(), 4, "wheelCount");

  return report("test_chassis");
}
