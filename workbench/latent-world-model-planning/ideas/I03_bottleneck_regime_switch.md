# I03：Latent-planning bottleneck relocation / regime law（2026-10-02）

- **状态：** SEED / common oracle & conditional independent mine
- **来源：** 近邻之间并不是一个简单“谁对谁错”的关系：
  - Temporal Straightening / CGS / DA-LeWM / Objective Bottleneck → metric/geometry；
  - SALT / Bilinear WM / one-step-not-a-WM → rollout/dynamics；
  - AD-WM / PhyLatent / Do-JEPA → counterfactual action effect；
  - IMWM / SAGE / LeFlow / parallel gradient planners → proposal/search；
  - Hidden Failure Modes → H/K/scoring-index / controllability interface；
  - Planning Limits / Anchored Planning / HWM → goal distance / temporal target。
- **研究动作：** oracle decomposition + design-space factorization + regime scan + success/failure case解剖。**默认角色是给 M1–M3 定位 bottleneck，不先假定自己是一篇 paper。** 只有形成跨任务 predictive regime law 才独立升级。

## 如果为真

> 这些方法不是在修一个固定 bottleneck。少数 **observable regime variables** 能预测 end-to-end ceiling落在哪一层，并因此预测哪一类 intervention有效。

候选变量优先：
- goal distance；
- candidate margin；
- planner-reachable fidelity；
- action-discrimination margin；
- H/K replanning ratio；
- candidate budget；
- local data support。

## 必须超过哪些近邻

| 近邻 | 已有 claim | I03 必须多走一步 |
|---|---|---|
| JEPA-WMs | broad recipe/design-space study | 不是更多sweep；要 oracle-identifiable bottleneck + predictive variable |
| Planning Limits | finite plannable range / far-goal limit | 预测何时 bottleneck从其它层迁到 horizon，不重复range curve |
| Hidden Failure Modes | H/K time-index mismatch + controllability interface | 把protocol layer作为control，并寻找跨layer regime law |
| P40 Control Theory | planner-reachable fidelity governs control better than data MSE | 将其作为observable候选，测试它何时成为binding predictor |
| What Must a WM Distinguish? | requirements依 query/candidate/planner | 在compact visual planning中给出可操作的 regime/intervention law |

## 不同结果

- **A：跨task出现稳定 signature switch，且同一个变量预先预测 intervention ranking** → E07，考虑 adaptive principle。
- **B：只有per-task阈值/故事** → benchmark，不升主张。
- **C：一个bottleneck几乎总主导** → 收敛到该层，生成更窄idea；这比硬做phase map更好。
- **D：H/K/scoring-index一控制，大部分“模型差异”消失** → 说明protocol解释更强；不把P57已知现象包装成新。
- **E：oracle ladder不稳定** → 修measurement，不铺方法矩阵。

- **决定性 pilot：** [E06](../experiments/E06_oracle_bottleneck_ladder.md)
- **confirmatory interaction：** [E07](../experiments/E07_interaction_regime_probe.md)
- **预期论文形态：** new regime law + adaptive principle，或 validated identification protocol。
- **排序（1–3）：** 证据 1 · 增量清楚度 2 · 形态匹配 3 · 成本 2 · 可完成性 2 · 不同结果信息增益 3
- **PARK条件：** 没有跨task predictive variable时，不把大矩阵包装成paper。