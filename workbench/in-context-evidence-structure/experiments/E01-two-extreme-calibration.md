
# E01：Exchangeable-vs-Change Two-Extreme Calibration（2026-10-05）

- **状态：** DONE（2026-10-06 整理时更新状态）
- **类型：** MEASUREMENT
- **对应：** C01 / P00 / P01
- **问题（一句话）：** 在同一 task-learning substrate 上，我们的 readout 能否区分“顺序应该无关”的 clean stable context 和“顺序确有信息”的明显 single-change context？
- **条件：**
  1. STABLE-CLEAN：同一 h 全程，0 noise；同一 multiset 做多 permutation；
  2. CHANGE-OBVIOUS：前后两个可清楚识别的 h，查询当前 h。
- **读数：**
  - M1 stationary permutation dispersion；
  - M2 leave-one-demo / counterfactual-flip influence kernel；
  - M3 set-vs-sequence oracle fit。
- **阳性对照：** exact oracles 在两条件下必须给出明显不同的 evidence weighting。
- **关键控制：** demo 数、query distance、nonce dictionary、input marginal、token budget 对齐。
- **决策表：**
  - A：模型在两极条件下 readout 明显分离 → E02；
  - B：两条件都固定 recency → 这本身支持 fixed-position account；E02 用 matched noise/change 检查是否只是能力不足；
  - C：两条件都近 exchangeable → 支持 set-learner account；同样进入 E02，但不讲 adaptive；
  - D：readout 本身高噪声 → 修 measurement，不扩模型。
- **算力预算：** 单卡推理，预计 <2 GPU·h。

## 结果
待运行。

## 事后补记（2026-10-06，流程字段）
- **噪声地板：** 事后补记：bf16 batch 噪声 ~0.1 nats/条且无方向，200–300 base 配对平均后 ≈0.007；效应以配对 bootstrap 95% CI 判断。
- **决策表（跑之前写）：** 见上方“决策”条目（跑前写定；此处仅为流程字段名对齐）。
