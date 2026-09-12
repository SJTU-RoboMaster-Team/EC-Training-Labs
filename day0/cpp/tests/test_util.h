#ifndef CPP_LAB_TESTS_TEST_UTIL_H
#define CPP_LAB_TESTS_TEST_UTIL_H

#include <cmath>
#include <cstdio>

// 极简测试框架，不用 gtest / catch2 —— 不给学生增加要装的东西。
// 和 HW1–HW5 那份工程的 tests/test_util.h 是同一套写法。

namespace test {

inline int g_passed = 0;
inline int g_failed = 0;

inline bool nearly(float a, float b, float eps = 1e-4f) {
  return std::fabs(a - b) < eps;
}

inline void ok(bool cond, const char* name) {
  if (cond) {
    ++g_passed;
  } else {
    ++g_failed;
    std::printf("[FAIL] %s\n", name);
  }
}

inline void eq_i(long got, long want, const char* name) {
  if (got == want) {
    ++g_passed;
  } else {
    ++g_failed;
    std::printf("[FAIL] %-28s got %8ld  want %8ld\n", name, got, want);
  }
}

inline void eq_f(float got, float want, const char* name) {
  if (nearly(got, want)) {
    ++g_passed;
  } else {
    ++g_failed;
    std::printf("[FAIL] %-28s got %8.2f  want %8.2f\n", name, got, want);
  }
}

inline int report(const char* suite) {
  std::printf("%s: %d/%d passed\n", suite, g_passed, g_passed + g_failed);
  return g_failed == 0 ? 0 : 1;
}

}  // namespace test

#endif  // CPP_LAB_TESTS_TEST_UTIL_H
