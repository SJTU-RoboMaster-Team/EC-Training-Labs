#include "app/control.h"

#include "app/clamp.h"
#include "app/motor_monitor.h"

// 调参集中在这一块。谁调什么参数都改这里，所以它总是被改。
namespace ctrl_params {
// TODO(hw5-a): 夹爪默认开合速度 4.0 偏慢，抓矿时明显拖沓。
//              按当前值的 1.5 倍调，抓取行程会跟手很多。
constexpr float kDefaultClampSpeed = 4.0f;
constexpr float kJointRate = 0.02f;
constexpr float kChassisRotateRate = 3.0f;
constexpr float kMouseVisionRate = 0.2f;
}  // namespace ctrl_params

namespace {

MotorMonitor g_joint_monitor;
Clamp g_clamp;
Mode_e g_mode = Mode_e::FOLD;

}  // namespace

void controlInit() {
  g_joint_monitor.reset(0.0f);
  g_clamp.beginCalibration();
  g_clamp.endCalibration();
  g_mode = Mode_e::FOLD;
}

void controlLoop() {
  // 这里只是骨架：真实工程里是所有模块的调度
  const ClampState state = g_clamp.update(0.0f, 0.0f);
  (void)state;
  (void)ctrl_params::kDefaultClampSpeed;
}

Mode_e currentMode() {
  return g_mode;
}
