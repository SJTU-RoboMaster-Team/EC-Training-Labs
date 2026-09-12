// 契约探针：构造函数必须允许不传 model。
//
// 出处 wheel-legged/base/motor/motor.h:70：
//   Motor(const Type_e& type, ..., 
//         float (*model)(const Motor&, const float&, const float&) = nullptr);
// 那个 `= nullptr` 是这条契约的核心：**回调可以为空**，
// 所以 setTorque 里必须先判空再调用。
#include <type_traits>

#include "base/motor/motor.h"

static_assert(std::is_constructible_v<motor::Motor, djimotor::RawData,
                                      motor::Type>,
              "Motor 必须能不带 model 构造（第三个参数要有 = nullptr 默认值）");
static_assert(std::is_constructible_v<motor::Motor, djimotor::RawData,
                                      motor::Type, motor::ModelFn>,
              "Motor 也必须能带 model 构造");
