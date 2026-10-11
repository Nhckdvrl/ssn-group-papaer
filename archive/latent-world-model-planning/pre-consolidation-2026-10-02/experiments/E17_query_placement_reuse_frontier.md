# E17 — Query placement × specialization/reuse frontier

- **Status:** PLANNED
- **Program/Idea:** R3 / I10
- **Goal:** 在同一 compact visual-world-model substrate 中，控制 query information 进入系统的层级，测 seen-query decision efficiency 与 unseen-query reuse 的 frontier。

## Minimal variants

优先复用已有模型，不一开始造新architecture：

1. **query-independent dynamics + query-only metric**；
2. **query-guided proposal + query-independent dynamics**；
3. **query-conditioned representation/head**（若已有近邻实现可复用）；
4. **query-conditioned dynamics**（只在前3者有清晰frontier时加入）。

## Queries

同一 dynamics / data 下构造：
- seen goals/objectives；
- unseen goal combinations；
- changed cost weights；
- same physics, new planner objective。

## Controls

- parameter count；
- training samples；
- query labels；
- candidate budget；
- planner H/K；
- representation capacity；
- task/query information budget。

## Readouts

- seen-query regret/success；
- unseen-query regret/success；
- candidate proposal efficiency；
- prediction reuse across queries；
- retraining / adaptation cost；
- query dimensionality vs retained predictive information。

## Gate

有价值的 pattern 不是“query-conditioning seen更强”——P38 已知。  
需要：
- query placement导致可重复的 specialization↔reuse frontier；
- frontier随 query complexity/capacity/planner stage系统变化；
- hold-out query/planner能预测。

若成立，再考虑 modular selective conditioning / capacity allocation。
