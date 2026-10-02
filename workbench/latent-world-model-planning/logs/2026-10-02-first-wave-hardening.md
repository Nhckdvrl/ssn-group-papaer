# 2026-10-02｜第一波 method hardening

本轮继续按“近邻是支点，不是禁区”的标准深挖 E16/E13。

## R1 / Planner-Boundary Branching (PBB)

新增直接压力：

- **FIRM-WM**：common-reset intervention branches 已直接用于 reward-free visual planning；所以我们的增量不能是“branch data 有用”，而是 **branch budget allocation**。
- **OnlineWM / Task-Sufficient WM / ToIA**：active/task-aware data acquisition 已有强近邻。
- **SPARK (ACL 2026)**：critical decision state dynamic branching 在 LLM-agent 训练已有独立工作。
- **TOM / Policy-Aware Simulator Learning / dual MPC**：policy-aware / active model learning 有更早思想祖先。
- **D-JEPA / AD-WM**：candidate decision / action discrimination 可直接优化。

当前最干净的假设：

> 同样新增环境 steps / resets 下，利用 latent MPC 的 elite-boundary / rank-instability 选择 same-state competing-action branches，是否比 random / coverage / global uncertainty / task-aware acquisition 更有效地降低 candidate regret 并提高 closed-loop success？

第一版只改数据采集位置，保持 LeWM / RC-aux 原目标不变；只有 data-only signal 成立后才考虑 ordinal / decision-aware loss。

## R2 / Planner-Stage Multi-Fidelity

新增直接压力：

- **Fast-LeWM**：parallel direct action-prefix prediction，且已有 self-consistency / decomposed terminal estimate。
- **DeepJEPA**：transition-level adaptive depth，公开 repo 截至本轮仍未 release 完整 code。
- **传统 robotics multi-fidelity planning**：cheap/fine model切换并非新思想。

因此当前 exact object 改成 **latent-CEM elite preservation**：

> 所有 candidates 先用 cheap direct prediction；只对“仍可能跨过 elite cutoff”的 candidates 支付额外 decomposed / recursive / refined prediction。能否在固定 wall-clock 下保住 FULL-REFINE 的 elite set 与 closed-loop performance？

最便宜 Stage A0 甚至无需训练新模型：Fast-LeWM 同一 checkpoint 的 direct score vs selective/full self-consistency。先测 candidate-bank elite recall、selected-action flips、refined-call fraction 和 wall-clock，再接 online CEM；信号成立后才训练 shared dual-fidelity head 或接 LeWM / DeepJEPA refinement。

## 状态

- GPU train runs = 0
- environment evaluation runs = 0
- science claim = 0
- 工作台仍为 PROPOSED

本轮只更新文献定位、idea与实验设计，不冒充本地结果。
