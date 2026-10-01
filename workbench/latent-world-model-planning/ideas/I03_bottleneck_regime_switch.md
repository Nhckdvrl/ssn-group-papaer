# I03：latent planning 的 binding bottleneck 是否存在可预测的 regime relocation？（2026-10-02）

- **状态：** SEED / second-priority mining engine
- **来源：** 2026 直接近邻对“为什么失败”给出多种不同答案：
  - geometry/objective：Temporal Straightening、CGS、DA-LeWM、Objective Is the Bottleneck；
  - representation/state/action effects：PhyLatent、AD-WM、PSG-JEPA；
  - dynamics/rollout：SALT、Bilinear WM、One-Step Next-Latent…；
  - search/proposal：IMWM、SAGE、LeFlow、RP1；
  - horizon/target：Planning Limits、Anchored Planning、HWM/FF-JEPA；
  - **protocol/interface：Hidden Failure Modes（terminal@H vs prefix@K/running cost，waypoint controllability）**；
  - theory：What Must a WM Distinguish?、A Control Theory of Predictability。
- **研究动作：** 设计空间分解 + oracle intervention + regime scan + interaction confirmation。

## 如果为真，足够强的主张

> 这些方法不是在解决一个固定、全局的“world-model quality”瓶颈。少数**可观测且预先定义**的 regime variables 能跨任务预测 binding bottleneck 落在 metric/representation、dynamics/action effect、proposal/search、horizon/target 或 planning protocol 哪一层，并因此预测哪类 intervention 有效。

这里的 novelty 不是“不同任务方法排序不同”，而是**predictive regime law**。

候选变量优先级：
1. goal distance / imagined-to-goal ratio；
2. candidate margin；
3. planner-reachable fidelity / data support；
4. counterfactual action-separation margin；
5. replanning ratio (K/H)；
6. action block / primitive-step horizon；
7. local transition coverage。

## 先加一个 protocol gate，否则整个 I03 都可能是假问题

Hidden Failure Modes 已表明：若 planner optimize (H) 但只 execute (K<H)，terminal-at-(H) cost 可能让同一 frozen model 看起来极差；prefix-at-(K) / running cost 可以大幅修复。

因此 E06 在归因 model layer 前必须比较：
- terminal@H；
- prefix@K；
- running/trajectory cost；
- fixed (H,K), action block；
- 同一 environment/model/checkpoint。

**能被这个 protocol correction 救掉的 failure 不标成 representation/dynamics bottleneck。**

## Failure signature

```text
Q = protocol / query-interface limited
R = representation / metric limited
D = dynamics / rollout limited
A = counterfactual action-discrimination limited
P = proposal / search limited
H = horizon / target-abstraction limited
M = mixed / unidentifiable
```

## 不同结果的信息增益

- **A：** 一个或少数 regime variables 跨任务预测 Q/R/D/A/P/H，并预测 intervention ranking → 形成 principle，进 E07；
- **B：** protocol Q 大量解释 failure → 说明过去 component comparison有混杂；可转成 evaluation/identification paper，但必须超过 P57 的 exact claim；
- **C：** 一个 layer 在所有合理 regime 都主导 → 收敛成更窄的 mechanism，不再做大 map；
- **D：** 每任务都要独立阈值 / post-hoc解释 → 只是 benchmark，PARK；
- **E：** oracle ladder replacement 本身不可复现 → 修 harness，不扩实验。

## 最近邻与 exact delta

| 近邻 | 已有 claim | I03 需要多走的一步 |
|---|---|---|
| JEPA-WMs | recipe/design-space empirical study | oracle-identifiable bottleneck + predictive regime variable，而非 sweep |
| What Must a WM Distinguish? | sufficiency depends on query/candidate/planner | 在真实 compact visual control 中给出可测 signature 与 intervention ranking |
| Planning Limits | finite plannable range even with perfect dynamics | 不重复 goal-distance effect；解释何时它成为 binding layer vs metric/search |
| Hidden Failure Modes | K/H / scoring-time / controllability interface 可改变 apparent quality | 把它作为 protocol gate；若 Q 是主结果，必须发现更一般的 regime law而非复制 terminal@H |
| AD-WM / DA-LeWM | elite-stage action/metric alignment | 把 elite margin/action discrimination作为 regime variable，不重新发明 metric |
| Control Theory Predictability | planner-reachable fidelity / off-manifold divergence | support/fidelity只是一个候选 variable，不把它当新机制 |

## 最便宜的决定性 pilot

[E06](../experiments/E06_oracle_bottleneck_ladder.md)

- **阳性对照：** 极低 candidate budget应触发 P；人为 (Kll H)+terminal@H 应能触发已知 Q；near goal + true dynamics应降低 H/D；可控 action collapse synthetic/known checkpoint 应触发 A。
- **噪声地板 + MIE：** oracle replacement带来的 paired regret/success 改善必须超过 E02 repeat floor；signature classification需要 bootstrap stability，不按 single episode定层。
- **决策表：** cross-task predictive variable → E07；per-task arbitrary → PARK；一个层始终主导 → 缩窄新 idea；Q/protocol dominate → 先对齐 protocol再重新评其它 layers。

## 顶会最低要求

- 至少两种 task regimes（topology + contact-rich）；
- 至少两种 model/substrate 或明确证明 law 与单一 architecture无关；
- protocol gate；
- oracle interventions；
- 预先定义 regime variable；
- confirmatory E07 interaction；
- 最终最好导出一个**不用 oracle test outcome**的 adaptive rule / training principle。

否则这只是一个很大的 benchmark matrix。

- **预期论文形态：** regime law + identification + adaptive principle；或者更窄的新 bottleneck机制。
- **排序打分（1–3）：** 证据 1 · 增量清楚度 2 · 形态匹配 3 · 成本 2 · 可完成性 2 · 不同结果的信息增益 3
- **PARKED 时：** 没有 cross-task predictive variable时明确 park，不靠增加 benchmark硬救。