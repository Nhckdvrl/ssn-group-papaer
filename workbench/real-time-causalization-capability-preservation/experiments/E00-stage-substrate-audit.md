# E00：公开 stage substrate / comparability audit（2026-10-02）

- **状态：** PLANNED
- **类型：** REPRO
- **对应：** territory D1 / D2
- **问题：** 是否至少有两条独立 interactive VWM lineage，公开了足够清楚的 bidirectional / causal / few-step / self-rollout stage checkpoints，使 capability-preservation 的 matched measurement 真正可做？
- **首选：** minWM（Wan2.1 1.3B、HY1.5 8B）与 ForgeWM。
- **读数：** checkpoint 可访问性；native inference；官方 metric reproduction；stage 间 scene/action pairing；VRAM / wall-clock / checkpoint size / I/O；哪些 stage change 是单因素、哪些是 bundle。
- **阳性对照：** 至少一个 checkpoint 复现作者 demo / native metric。
- **混杂审计：** attention regime、sampling steps、training data、history source、action interface、checkpoint provenance 必须逐项登记。
- **决策表：**
  - ≥2 lineage 可跑且可配对 → 注册 E01 common capability baseline；
  - 只有 1 lineage 干净 → 不做跨-lineage claim；
  - checkpoint/evaluator 不足 → 立足点失败，回人审，不通过大训练制造实验对象；
  - 已有 prior 用同一 capability suite 做了同样 factorized attribution → 更新 positioning，重新找 delta。
- **预算：** metadata 0 GPU；smoke ≤10 GPU·h；I/O 单独记录。

## 结果
待执行。
