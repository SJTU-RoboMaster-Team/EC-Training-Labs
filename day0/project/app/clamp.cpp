#include "app/clamp.h"

void Clamp::beginCalibration() {
  is_calibrating_ = true;
  state_ = ClampState::kIdle;
}

void Clamp::endCalibration() {
  is_calibrating_ = false;
}

ClampState Clamp::update(float force, float angle) {
  // TODO(hw5-b): 标定的时候电机会顶到限位，阻力直接超过阈值，
  //              被误判成"夹到东西了"，标定流程反复被打断。
  //              标定期间不应该做阻力判断。
  if (force > kResistThreshold) {
    state_ = ClampState::kBlocked;
    return state_;
  }

  if (angle > kOpenAngle) {
    state_ = ClampState::kHolding;
  } else {
    state_ = ClampState::kMoving;
  }
  return state_;
}
