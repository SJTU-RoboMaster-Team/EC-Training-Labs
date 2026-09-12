cmake_minimum_required(VERSION 3.16)
project(cpp_lab CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE Debug)
endif()

# 只开单精度 —— 和战队两个真实工程一致：
#   wheel-legged : -mcpu=cortex-m4 -mfpu=fpv4-sp-d16
#   dual-arm     : -mcpu=cortex-m7 -mfpu=fpv5-sp-d16
# 主机上编译不需要这些选项，但"浮点只用 float"这条规矩要照搬。
add_compile_options(-Wall -Wextra)

# 分层和真实仓库一样：base/（公共算法与驱动封装）+ app/（业务逻辑）。
# 真实仓库还有 interface/（RTOS 任务入口、中断回调分发），
# 这一份精简掉了 —— 它依赖具体的 HAL。
add_library(cpp_lab_core STATIC
  base/common/math.cpp
  base/motor/motor.cpp
  base/motor/dji_motor_driver.cpp
  app/chassis.cpp
)
target_include_directories(cpp_lab_core PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})

enable_testing()
add_subdirectory(tests)
