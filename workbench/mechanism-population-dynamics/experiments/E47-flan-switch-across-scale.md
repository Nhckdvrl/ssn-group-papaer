# E47：Flan 装入的 “Question:” 开关在 60M–750M 是否也存在？（2026-10-03）

- **状态：** PLANNED
- **类型：** CLAIM（C04 的尺寸广度；同时为 E48 的线索替换训练干预选尺寸）
- **对应：** C04（目前只在 1B：DataDecide + OLMo 2）；A02 §2；对标 Goyal ICLR 2025 / Kim ACL 2026（多模型尺度）
- **问题（一句话）：** 在 DataDecide 的 60M / 90M / 150M / 300M / 530M / 750M 上，有 Flan 与无 Flan（dolma1_7 vs dolma1_7-no-flan）的模型，是否同样只在 “Question:” 线索下出现上下文采信差异？
- **设置：**
  - 模型：每个尺寸 dolma1_7 与 dolma1_7-no-flan × default / small-aux-2 / small-aux-3（不要求共用初始化）；步数取每个 seed 下两个配方共有的最大步，且不超过 default 的最终步（150M 的 aux seed 步数结构异常，按此规则取）。
  - 读数：E32 的 7 个单元（decl、A_only、Q_only、QA、QA_short、novel、incongruent），采信边际 lp(dist) − lp(ans)；线索效应 = 单元 − decl；条目 = 该尺寸 6 个模型共同已知的条目（clean prompt 上 lp(ans) > lp(dist)），类别等权（每类 ≥ 10 条才计入）。
  - 脚本：`scripts/e47_flan_scale.py`。
- **读数：** 每个尺寸、每个单元的 Flan − no-Flan 差 Δ，SE = √((var_Flan + var_noFlan) / 2) × √(2/3)（每边 3 seed，同 E29）。
- **阳性对照：** 1B 的结果（E32：QA +2.43，SE 0.79）作为参照；每个尺寸共同已知条目 ≥ 100 条（否则该尺寸不可判定）。
- **噪声地板 + MIE：** Δ > 2·SE。
- **混杂审计：** 小模型已知条目少，共同已知集合随尺寸变化（报告 n）；不同 seed 的训练比例不同（750M aux 43%），开关在 1B 上 3.6% 即出现（E29），写明；读数与 E32 完全相同。
- **决策表（跑之前写）：**
  - 某尺寸 QA 或 Q_only 的 Δ > 2·SE，且 decl 水平差不显著 → 该尺寸有开关；C04 写成“从 X 到 1B 都存在”。
  - 所有更小尺寸都无开关 → C04 写成“在 ≥ 1B 出现”，并报告最大的无开关尺寸（提示开关依赖容量）。
  - **E48 选尺寸：** 取有开关的最小尺寸（≥ 300M 优先，以降低训练成本）；若只有 1B 有开关，E48 在 1B 上做。
- **算力预算：** 36 个模型 × 2–5 分钟 ≈ 2 GPU·时；下载约 50 GB　**实际：**

## 结果（跑完后填写）
