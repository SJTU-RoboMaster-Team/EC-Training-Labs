#include "base/common/math.h"

// ⚠️ TODO(cpp1)：这个文件是空的，所以链接会报一串 undefined reference。
//
// 这就是 HW3 里你见过的那条报错 —— 只不过这次是你自己造成的。
//
// 为什么编译能过、链接才报：
//   编译 math.cpp 时，编译器只看到 math.h 里的**声明**；
//   语法和类型都对，所以编译通过。
//   链接时才发现：没有任何一个 .o 里有这些符号的定义。
//
// 你要做的：把 math.h 里声明的四个函数在这里实现。
// （这个文件已经在 CMakeLists.txt 的 add_library 列表里了，不用改构建。）
