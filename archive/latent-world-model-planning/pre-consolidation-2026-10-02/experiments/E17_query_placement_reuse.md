# E17 — Query placement × reuse pilot

- **状态:** PLANNED
- **对应:** I10 / R3
- **目的:** 在同一 compact WM stack 中控制 query 注入位置，测 specialization–reuse frontier。

## Minimal variants

保持 encoder/predictor total params近似匹配：

- Q0: query-independent dynamics；query只进 test-time cost
- Q1: query进 metric/verifier
- Q2: query进 proposal；dynamics仍通用
- Q3: query-conditioned dynamics / representation

首轮不超过4 variants。

## Query regimes

- seen goals/rewards
- unseen recombination
- changed planner cost
- changed candidate generator

如果有 language query，后续再加，不作为首轮依赖。

## Measurements

- seen-query success / regret
- unseen-query success / regret
- predicted-trajectory reuse
- candidate sample efficiency
- model calls / latency
- capacity utilization
- query-conditioned feature drift

## Critical controls

- same offline data
- same query train split
- same total params / optimization budget
- task-specific heads parameter count separate
- no test query leakage

## Gate

- Q3 seen强、unseen弱但完全复制 P38 setting → 不升级；
- injection layer ranking随 query complexity / capacity / planner change有稳定 switch → strong signal；
- Q2 modular proposal接近Q3 seen效果且保Q0 reuse →可能形成方法/原则；
- second task structure复现后才大铺。

## 结果
未运行。
