# E13 — Explicit vs implicit predictive structure: matched pilot

- **状态：** PLANNED after substrate parity
- **对应：** I08 / M2
- **对象：** explicit JEPA-WM（优先 JEPA-WMs/LeWM family） vs Bagatella TD-JEPA implicit predictive representation；hybrid仅作为后续。
- **第一原则：** 不把两篇原论文主表直接比较。
- **common audit：**
  - 同 offline dataset revision；
  - 同 observation modality；
  - 同 train/test goal/reward definitions；
  - environment真实utility统一；
  - 分别报告 native protocol 和 common protocol；
  - train steps/GPU-hours/peak VRAM + deployment model calls/wall time。
- **最小 regime grid：**
  1. in-distribution goal/reward；
  2. reward/goal redefinition（same dynamics）；
  3. environment/layout/dynamics shift；
  4. near vs far horizon。
- **问题不是“谁赢”，而是：** 相对优势能否由 goal/reward shift、horizon、test compute等变量解释，并在 hold-out regime预测。
- **gate：** 只有形成跨至少两个环境的稳定 regime signature才扩展；如果结果只跟训练预算走，记录后停止。
