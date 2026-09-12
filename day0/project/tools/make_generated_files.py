#!/usr/bin/env python3
"""生成「IDE 打开工程时会自己产生」的那些文件。

为什么需要它：Keil 一打开工程就会生成调试配置、RTE 组件、窗口布局这些文件，
而**它们每次打开都会变，不该进版本库**。你在 HW5 里要处理的就是这件事。

但你现在未必开着 Keil，所以这个脚本把那几种文件直接造出来，
让你能看到"`git status` 里冒出一堆陌生文件"的真实情形。

用法（在 day0/project/ 下）：

    python tools/make_generated_files.py

可以重复运行。
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

FILES = {
    "mcu/stm32f407/MDK-ARM/DebugConfig/day0_STM32F407VG.dbgconf": """\
# Keil 调试配置。由 IDE 生成，每次换调试器都会变。
Dp_Init = 1
Dp_Reset = 1
Dp_Halt = 0
""",
    "mcu/stm32f407/MDK-ARM/RTE/_day0/RTE_Components.h": """\
/* 由 Keil Run-Time Environment 自动生成，不要手改 */
#ifndef RTE_COMPONENTS_H
#define RTE_COMPONENTS_H

#define RTE_DEVICE_STARTUP_STM32F4XX

#endif /* RTE_COMPONENTS_H */
""",
    "mcu/stm32f407/MDK-ARM/day0.uvguix.zhangsan": """\
<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
<!-- Keil 保存的窗口布局。每个人打开过的窗口都不一样，所以它总是变。 -->
<Layout>
  <Window Name="Project" Left="0" Top="0" Width="280" Height="600"/>
  <Window Name="Editor" Left="280" Top="0" Width="900" Height="600"/>
</Layout>
""",
}


def main() -> int:
    print("生成 IDE 自己会产生的那几个文件：")
    for rel, content in FILES.items():
        path = ROOT / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8", newline="")
        print(f"  {rel}")
    print()
    print("现在跑：")
    print()
    print("    git status")
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
