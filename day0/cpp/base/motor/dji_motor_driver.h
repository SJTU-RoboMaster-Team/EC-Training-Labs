#ifndef CPP_LAB_BASE_MOTOR_DJI_MOTOR_DRIVER_H
#define CPP_LAB_BASE_MOTOR_DJI_MOTOR_DRIVER_H

#include <cstdint>

// DJI 电调（M3508 / M2006 / GM6020）的 CAN 打包与解析。
//
// 抽象自真实仓库：
//   wheel-legged/base/motor/driver/dji_motor_driver.h:24    typedef enum / typedef struct
//   wheel-legged/base/motor/driver/dji_motor_driver.h:44    RawData_t
//   wheel-legged/base/motor/driver/dji_motor_driver.cpp:68  移位打包
//
// 官方协议（C620 电调，详见 Day 3 的 CAN 课）：
//   反馈帧 ID = 0x200 + 电调 ID，DLC = 8，大端
//     DATA[0..1] 转子机械角度  uint16  0~8191 对应 0~360°
//     DATA[2..3] 转子转速      int16   rpm
//     DATA[4..5] 实际转矩电流  int16
//     DATA[6]    温度          uint8   摄氏度
//     DATA[7]    保留
//
//   控制帧 ID = 0x200（ID 1~4）/ 0x1FF（ID 5~8）/ 0x2FF（ID 9~11），DLC = 8
//     每个电机占 2 字节，高字节在前
//     DATA[2i]   = intensity >> 8
//     DATA[2i+1] = intensity

namespace djimotor {

// 真实仓库用的是 C 风格 typedef：
//   typedef enum CANIDRange { ID_1_4, ID_5_8, ID_9_11, } CANIDRange_e;
// 新代码更推荐 enum class。两种你都会在战队仓库里看到。
enum class CANIDRange : uint8_t {
  ID_1_4 = 0,     // 电调 ID 1~4，控制帧 0x200
  ID_5_8 = 4,     // 电调 ID 5~8，控制帧 0x1FF
  ID_9_11 = 8,    // 电调 ID 9~11，控制帧 0x2FF
};

// 电调反馈的原始数据
struct RawData {
  uint16_t ecd = 0;              // 编码器值(0~8191)
  int16_t rotate_speed_rpm = 0;  // 转速(rpm)
  int16_t torq_current = 0;      // 转矩电流
  uint8_t temp = 0;              // 温度(摄氏度)
};

// 从 8 字节反馈帧里解出 RawData。
//
// ⚠️ TODO(cpp4)：实现它。
//   要求：
//     · 字段是**大端**（高字节在前），C620 官方协议规定的
//     · 用位运算拼，别用 memcpy 把 struct 直接盖上去 ——
//       想一想 struct 的对齐（padding）会出什么问题
//     · 返回值是 RawData，不是指针（值语义，和真实仓库一致）
//     · 有符号字段（转速、转矩电流）先拼成 uint16 再转 int16
RawData parseRawData(const uint8_t data[8]);

// 把 4 个电机的控制量打包成 8 字节：intensity[i] → out[2i] / out[2i+1]，高字节在前。
//
// ⚠️ TODO(cpp4)：实现它。
//   真实代码是这么写的（dji_motor_driver.cpp:72）：
//       can_tx_data1_[2 * i]     = (motor->intensity_ >> 8);
//       can_tx_data1_[2 * i + 1] = (motor->intensity_);
//   想一想：第二行为什么不用 & 0xFF？如果 intensity 是负数会怎样？
void packControl(const int16_t intensity[4], uint8_t out[8]);

}  // namespace djimotor

#endif  // CPP_LAB_BASE_MOTOR_DJI_MOTOR_DRIVER_H
