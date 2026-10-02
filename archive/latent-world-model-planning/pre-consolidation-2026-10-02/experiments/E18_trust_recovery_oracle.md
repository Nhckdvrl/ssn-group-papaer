# E18 — Which recovery action should a planner take when imagination is unreliable?

- **Status:** PLANNED
- **Program/Idea:** R5 / I11
- **Type:** released-checkpoint / evaluation-first pilot

## Question

不是“能不能检测 world-model error”，而是：
> **不同 reliability/failure signals 是否能预测哪种 recovery action 真正提高环境 utility？**

## Recovery actions

只选已经有成熟实现的少数动作：
- continue native planning；
- shorter horizon / more frequent replanning；
- increase search/candidate budget；
- feedback correction（若现成可接）；
- lightweight adaptation（若现成可接）；
- fallback learned proposal/policy/intuition（有资产时）。

不需要首轮全部具备。

## Conditions

建立 failure/regime bank：
- near vs far goal；
- low vs high candidate margin；
- visual shift；
- dynamics shift；
- low-support action；
- long open-loop rollout。

## Signals

已有成熟指标优先：
- ensemble/disagreement；
- planner-reachable fidelity / support；
- rollout consistency；
- predicted-vs-observed residual；
- candidate margin；
- reachability confidence；
- model-vs-intuition disagreement。

## Oracle table

对同一个 planning state，离线/可reset地执行各 recovery action，得到：
- utility lift；
- extra model calls；
- wall clock；
- selected-action regret。

定义 oracle best intervention，问 signal 能否预测它。

## Gate

- 一个 intervention几乎总赢 → 做该baseline，不搞router；
- signals只预测“模型差”，不能预测“怎么修” → 不升级；
- failure family决定不同 intervention winner，且简单observable能跨task预测 → I11 PROMISING；
- 再长 training-free router / adaptive compute policy。
