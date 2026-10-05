# E30：event-boundary-versus-participant-contrast（2026-10-05）

- **状态：** PLANNED / RUNNING / DONE / VOID（作废需写原因）
- **类型：** CLAIM（推进主张）/ PILOT（idea 的决定性实验）/ REPRO（基线复现）/ EXPLORE（baseline gate 之后的自由探索；默认预算见 EXECUTION.md）
- **对应：** 主张 C## / idea I## / 痛点 P##（至少一个）
- **问题（一句话）：**
- **设置：** 模型与版本、数据与切片、配置文件、种子数、n、命令
- **读数：** 指标定义；是否与被测变量解耦（选窗 / 采样 / 自校准）
- **阳性对照：** <工具在已知有效应处能测到>
- **噪声地板 + MIE：** <重复测量或种子方差；多大效应才会改变决策 / 科学解释；2×noise 仅可作 pilot heuristic>
- **混杂审计：** 见 `workbench/EXECUTION.md` §4，逐项写“无关 / 已控制 / 未控制（原因）”
- **决策表（跑之前写）：** 结果 A → ；结果 B → ；不确定 →
- **算力预算：** <GPU·时估计>　**实际：** <GPU·时>

## 结果（跑完后填写；不改上面的内容，修改需注明日期）
- 数字（含 CI / 种子方差）：
- 结果文件：`results/...`
- 按决策表执行了什么：
- 主张变化：C## Lx → Ly
- POST-HOC 分析（事后才想到的，单独标注）：
