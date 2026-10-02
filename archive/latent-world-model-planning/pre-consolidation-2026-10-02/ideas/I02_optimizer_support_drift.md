# I02：Optimizer-induced support drift / false elites（2026-10-02）

- **状态：** PARKED（保留 E05 作为 I03 / diagnostics，不再作为独立第一梯队 paper seed）
- **来源：** 最初来自 PLDM uncertainty、Hi-LeWM search-distribution mismatch、ACID/MEND 以及经典 offline MBRL model exploitation。第二轮深挖后，**A Control Theory of Predictability in Latent World Models (arXiv:2607.10362)** 已直接把 planner-reachable distribution、off-manifold divergence 与 plan-cost discrepancy形式化，并实证 data-averaged prediction error 与 control 解耦；因此原来“CEM 把 candidate 推离 data support → model optimism → regret”的 broad story compression risk 太高。
- **研究动作：** 从独立 idea 降级为 I03 的定位工具 / 反事实 measurement。
- **若未来重开，必须比现有 theory 多什么：** 不能只是再画 support vs error 曲线。必须出现一个**该 control-theory fidelity / uncertainty / classic model-exploitation baselines 解释不了的 planner-stage-specific mechanism**，并导出不同 intervention。

## 仍值得保留的 measurement

E05 可以继续作为共享资产，在 I03 需要判断“proposal/search layer 是否成为 bottleneck”时记录：
- CEM iteration；
- behavior action-chunk support；
- ensemble disagreement（若可用）；
- predicted-vs-real plan cost；
- false-elite rate；
- candidate regret；
- action norm/smoothness。

但它默认不产生新 C##。

## 最近近邻与压力

| 近邻 | 已占 claim | 对 I02 的影响 |
|---|---|---|
| A Control Theory of Predictability | planner-reachable measure / off-manifold divergence governs control more directly than data-average error | broad support-drift story基本被压缩 |
| PLDM | ensemble uncertainty penalizes OOD transition | uncertainty baseline不可省 |
| MOPO/MOReL 等 offline MBRL | model exploitation / support penalty | “OOD planner exploits model”是经典 |
| Hi-LeWM | search distribution mismatch in macro-action/hierarchical setting | distribution mismatch 已在同领域显式出现 |
| ACID / MEND | consistency / latent hallucination diagnostics | detector/reranker 空间也已有直接近邻 |

## 重开条件

满足至少一条：
1. E05 在强 controls 下发现 **CEM stage-wise process** 中一个稳定 failure law，而 P40 的 planner-reachable fidelity / ensemble uncertainty不能预测；
2. I03 发现某个 regime 中 support drift 是唯一 oracle-identifiable bottleneck，并且现有方法无法修；
3. 一个简单、可验证的 intervention 只作用于这个机制，并跨 ≥2 tasks / model families 有一致后果。

否则保持 PARKED，不因为有空闲 GPU 单独扩 seed。

- **预期论文形态（若重开）：** 新 planner-induced failure mechanism + intervention，而非“offline model exploitation again”。
- **重开时最便宜实验：** [E05](../experiments/E05_cem_support_drift.md)。
- **排序打分（当前）：** 证据 1 · 增量清楚度 1 · 形态匹配 2 · 成本 3 · 可完成性 3 · 不同结果信息增益 2。