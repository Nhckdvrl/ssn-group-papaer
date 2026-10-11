# I12 — Equal-budget data value for actionable world models

- **Program:** R1 — data & identifiability
- **状态:** SEED
- **目的:** 比 I09 route imprint 更宽。问：

> **固定 interaction / transition budget 时，什么样的经验最能提高 world-model planning utility？**

## Data families

至少区分：

1. state coverage
2. conditional action excitation
3. route / trajectory diversity
4. same-state counterfactual action branches
5. failure / recovery transitions
6. active disagreement / decision-boundary probing

## Why this is not PLDM v2

PLDM研究 data quality/diversity/stitching 对 model-based/model-free performance 的影响。

I12 只有在做出更强 decomposition 才有价值：

- same transition budget；
- measurement of representation / transition identifiability；
- candidate-level planning utility；
- data family之间的 marginal value / interaction；
- 找出 environment/planner regime 下最值得收集的数据。

## 直接近邻

- P94: conditional action excitation
- Do-JEPA / FIRM: intervention branches
- Task-Sufficient WM: active probing
- OnlineWM: error-targeted active querying + same-state counterfactual action contrasts
- PLDM: quality/diversity/stitching
- WorldTest: environment-level query support
- offline MBRL uncertainty / coverage literature

## First seed

先不做所有6类。

选：
- passive expert-ish trajectories
- action-excited trajectories
- multi-route trajectories
- same-reset action branches（若环境支持）

每组严格 equal transition budget。若加入 OnlineWM-style adaptive querying，需要同时报告 **simulator query adaptivity**（因为同样transition数不等于同样 acquisition power）；可做 fixed-policy version 与 adaptive version分表。

读数：
- on-policy prediction
- counterfactual action error
- planner candidate regret
- closed-loop success
- environment/query coverage

## 可长出的 narrative

- action excitation是 necessary but not sufficient；
- route diversity对 long-horizon planning 的边际价值超过额外IID transitions；
- same-reset branch数据只在 low-excitation regime高价值；
- active data collection应该 targeting decision boundary，而不是 average prediction error；
- data-type ranking随 horizon / contact / query flexibility变化。

## 最大 compression

“data diversity当然重要。”

所以必须得到 **specific, predictive, cross-regime data-value law**。

## 对应实验
E16。
