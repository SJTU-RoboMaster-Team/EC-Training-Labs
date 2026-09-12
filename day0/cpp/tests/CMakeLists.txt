# 一个测试一个可执行文件 —— 和 HW1–HW5 那份工程保持一致，
# 这样 grader 找 test_* 的逻辑可以完全复用。
foreach(t math can motor chassis)
  add_executable(test_${t} test_${t}.cpp)
  target_link_libraries(test_${t} PRIVATE cpp_lab_core)
  add_test(NAME test_${t} COMMAND test_${t})
endforeach()
