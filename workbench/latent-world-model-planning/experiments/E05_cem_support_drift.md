# E05：Conditional planner-reachable fidelity / support diagnostic（2026-10-02）

- **状态：** PLANNED
- **类型：** EXPLORE（**CONDITIONAL — 不自动运行**）
- **对应：** I02（PARKED）；只在 I03/E06 需要区分 search/off-manifold layer 时触发
- **触发条件：** E06 显示 true-dynamics / proposal/search replacement 有明显收益，且需要判断是不是 planner-reachable/off-support fidelity；否则不消耗 GPU。
- **背景 ownership：** A Control Theory of Predictability 已 formalize planner-reachable measure / off-manifold divergence 与 plan-cost discrepancy；PLDM 有 ensemble uncertainty；offline MBRL model exploitation经典。E05 默认是 diagnosis，不是 paper claim。

## 问题

在被 E06 触发的 regime 中，CEM stages 的 candidate distribution 是否进入 fidelity较低区域；而这个已知 planner-reachable fidelity / uncertainty 能否解释 false elites / environment regret？

## 设置

固定 model/checkpoint/start-goal/planner protocol。对每个 CEM stage 保存 candidate；对预注册 stratified subset做 simulator replay。

support/fidelity至少：
1. behavior action-chunk kNN 或 density；
2. state/history-conditioned BC log-likelihood（若可训练且validation可靠）；
3. ensemble disagreement（已有 PLDM-style ensemble时）；
4. **P40-style planner-reachable fidelity / predicted-vs-true plan-cost discrepancy**，在 replay可得时优先。

## 读数

- planner stage；
- support/fidelity；
- prediction/plan-cost discrepancy；
- false-elite rate；
- candidate regret；
- action norm/smoothness/bounds；
- selected outcome；
- optional ACID/MEND score。

## 阳性对照

- 由数据动作加噪/替换生成显式远-support candidate，support metric应下降；
- 人为已知 dynamics error candidate必须被 plan-cost discrepancy捕获；
- 若 ensemble/BC metric 连显式 OOD都不区分，不用它解释真实 CEM。

## 噪声地板 + MIE

bootstrap over planning decisions/start-goal。  
E05 只有在：
- P40-style fidelity / uncertainty 的解释仍留下稳定 residual mechanism；
- 或一个 metric能跨 ≥2 task/regime预测 oracle-identified search ceiling，
才可能触发 I02重开讨论。

## 混杂审计

- stage 与 action magnitude/smoothness共同控制；
- candidate budget/compute固定；
- support metric不用 test utility训练；
- candidate replay subsample跑前固定；
- H/K/score timing固定；
- model checkpoint固定；
- planner seed记录。

## 决策表

- P40 fidelity / ensemble uncertainty已经解释 E06 search signature → **结束 E05，I02保持 PARKED**；
- support只与 action magnitude共变 → 当前 mechanism不成立；
- false elite存在但 support/fidelity都不解释 → 回 I03 的 metric/dynamics/action-discrimination层；
- 出现稳定 residual planner-stage law + distinct intervention → 提交人审后才重开 I02。

- **算力预算：** evaluation为主；只有 E06触发才填。  
- **实际：** 待运行

## 结果
未运行；条件未触发。