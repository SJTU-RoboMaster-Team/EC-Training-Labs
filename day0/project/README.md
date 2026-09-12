# day0 / project

这是 Day 0 作业链 **HW1–HW5 共用的 C++ 工程**。五份作业都在它上面做，
所以你会一步步看到自己的改动累积成一段历史。

**任务书不在这里**，在上一级：

```text
../homework/hw1-build.md
../homework/hw2-encoder.md
../homework/hw3-link.md
../homework/hw4-format.md
../homework/hw5-git.md      ← Git 工作流（本篇已写完）
```

## 快速验证环境

```bash
cd day0/project
python tools/build.py
```

正常的话你会看到 `test_clamp` 通过、`test_encoder` **失败 1 个用例** ——
那是 HW2 要修的东西，现在失败是对的。

## 目录

```text
app/      业务模块（control / arm / motor_monitor / clamp）
base/     底层（电机数据结构、数学工具）
tests/    单元测试
tools/    build.py（构建+测试）、make_generated_files.py（HW5 用）
mcu/      STM32F407 的 Keil 工程
```
