# E16 — Equal-budget data value decomposition

- **状态:** PLANNED / conditional on R1 remaining strong
- **对应:** I12 / R1
- **目的:** 固定 data budget，分解不同 experience type 对 actionable planning 的边际价值。

## Stage 0 — one environment

优先 topology + resettable simulator。

构造 equal-transition-budget datasets：

- D0 baseline behavior
- D1 action-excited
- D2 route-diverse
- D3 same-state counterfactual branches（若可行）

保持：
- total transitions
- start-goal distribution
- observation/render config
- model capacity/steps

记录：
- state coverage
- conditional action covariance / P94 excitation
- route entropy
- branch count per state
- path-efficiency distribution

## Model side

首轮只 LeWM/one compact explicit WM。
先回答“哪类data改善 controlled model + planning”。

若现象强，再加 RC-aux / Temporal-Distance JEPA 判断 planning-aligned objective 是否改变 data ranking。

## Readouts

1. ID one-step error
2. counterfactual action prediction under simulator branches
3. rollout error
4. fixed candidate ranking/regret
5. closed-loop success
6. environment-level query coverage（能支持时）
7. GPU-hours / data-generation cost

## Key analysis

不只单因素主效应。

至少看两个 interaction：
- action excitation × route diversity
- passive coverage × counterfactual branch data

目标是发现 **data family 的 complementarity / substitutability**。

## Gate

- 所有差异只跟state coverage走 → 退化为普通coverage result；
- counterfactual branches只等价于更多samples → 不升级；
- 存在跨seed、second task的 data ranking / interaction → 升I12；
- 最好能用简单 observable（excitation, route entropy, horizon）预测哪类data最值钱。

## 结果
未运行。
