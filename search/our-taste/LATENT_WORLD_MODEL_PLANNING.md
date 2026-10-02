# Territory 卡：紧凑潜在世界模型与规划

日期：2026-10-02。通道：our-taste。状态：**PROPOSED / problem-led literature+code-hardened / execution-ready；不是 candidate。**

工作台：[latent-world-model-planning](../../workbench/latent-world-model-planning/README.md)；资源：[RESOURCES](../../RESOURCES.md)。  
科学主入口：[RESEARCH_MINES](../../workbench/latent-world-model-planning/RESEARCH_MINES.md)。  
领域 authority：[PAPER_LINEAGE](../../workbench/latent-world-model-planning/PAPER_LINEAGE.md) · [LITERATURE_LEDGER](../../workbench/latent-world-model-planning/LITERATURE_LEDGER.md) · [PROBLEM_METHOD_MAP](../../workbench/latent-world-model-planning/PROBLEM_METHOD_MAP.md) · [POSITIONING](../../workbench/latent-world-model-planning/POSITIONING.md)。

## 1. 为什么保留

不是因为“小模型容易跑”，而是这里同时满足：

1. **母问题够大。** 顶会/强期刊已经连续把 representation geometry、decision sufficiency、counterfactual action effect、partial observability、planning search、temporal interface、offline data semantics 当作核心问题。
2. **仍存在互相没有统一的 scientific pressures。** 2026 论文分别把瓶颈放在 representation / dynamics / objective / search / belief / data / query interface；不是一个“再刷点benchmark”的成熟死区。
3. **实验可识别。** offline trajectories + resettable simulator + candidate-level planner允许 oracle replacement、same-state intervention、fixed-candidate regret，而不只看最终success。
4. **资源高度适配。** compact models和独立实验可单卡/单节点；大量GPU用于 conditions × seeds × environments × ablations，而不是多节点大训练。
5. **方法可以从问题长。** RC-aux、SALT、Temporal Straightening、FIRM-WM等强工作都不是“先有锤子”，而是把一个真实 mismatch 压成可操纵对象后再做很小的 correction。

## 2. 不做什么

不能把这些当 headline：

prediction≠planning；L2≠progress；generic reachability；generic multi-step；generic inverse/physical grounding；“不同action future要可分”；CEM会OOD；long horizon难；subgoal/hierarchy；closed-loop比open-loop重要；POMDP需要history；false negatives存在。

这些都只能是 background / baseline / measurement。

## 3. 当前三个 problem mines

### M1 / I07 — Observable goal ≠ control state

image-goal指定的是**可观测目标配置**，但 action consequence可能依赖隐藏 velocity / contact / friction / regime。真正的问题是：

> 同/近同 observation 对应不同 hidden dynamics 时，是否会改变真实最优 candidate action？deterministic history何时够，何时需要 belief / multi-hypothesis uncertainty？

FIRM-WM、UWM-JEPA、Flow Equivariant WM、I-TAP 已占 factorization/belief/memory的 broad story，所以 E11 必须先证明 **actionable aliasing → candidate regret → closed-loop consequence**。

### M2 / I08 — Explicit rollout vs implicit predictive abstraction

TMLR 2026 JEPA-WM study明确区分：
- explicit action-conditioned dynamics + test-time CEM/MPPI/GD；
- Bagatella TD-JEPA式 implicit long-horizon successor representation + amortized policy；
- TD-MPC2式 hybrid；

并把 training/inference/generalization trade-off 的直接比较留作 future direction。

我们的目标不是排行榜，而是找：

> reward/goal redefinition、dynamics/layout shift、horizon、data coverage、counterfactual-query需求、deployment compute 能否预测 explicit / implicit / hybrid 的 regime frontier？

E13 是 matched pilot。

### M3 / I09 — Behavior trajectories ≠ environment controllability

RC-aux / Bai-Xiong Temporal-Distance JEPA 从 trajectory order/gap/cross samples 学 planning semantics；QRL/CGCIVL/PLDM 已说明 behavior statistics 与 optimal control/connectivity不是同一件事。

真正未决的是：

> 在相同 environment dynamics 下，**真实改变 generating behavior policy** 后，planning-aware latent WM 是否把 behavior route/tempo 写进 deployed reachability/progress geometry，并改变 MPC candidate ranking与closed-loop control？

E14 必须控制/量化 coverage/local support；旧 E03/E04 只是重切 episode、loss看不到 treatment，已 VOID。

## 4. 子诊断

- **I06 / E08–E10**：semantic negatives vs global geometric regularization。保留，但已降为 M3 slice；generic“negative distortion”不是论文。
- **I03 / E06–E07**：oracle bottleneck ladder。是三条mine共用的定位仪器；只有出现cross-task predictive regime law才独立升级。
- I05 generic POMDP/context sweep 已被 I07 supersede。

## 5. 执行

```text
E00 smoke
  ↓
E01 baseline + replay/candidate logger
  ├─ E11 → conditional E12       M1
  ├─ E14 → conditional E15       M3
  │      └─ E08/E09/E10          M3 subdiagnostic
  └─ E13 → hold-out regime test  M2

E02/E06 = common decision/oracle calibration
E03/E04 = VOID
```

第一轮三个 mine 都只跑**便宜的 proof-of-problem**；哪一条先出现自然、稳定、对decision load-bearing的 pressure，再用多GPU大面积铺开。

## 6. 顶会升级标准

至少形成：
- 一个领域真实问题中的 **new distinction / failure law / regime boundary**；
- candidate/action/closed-loop consequence；
- 对强近邻的 exact delta；
- controlled identification，能排除普通coverage、compute、H/K、search budget等解释；
- 若需要方法，方法是 diagnosis 的最小自然后果，而不是“加一个loss涨点”。

更多seed、更多benchmark、漂亮probe、单个toy anomaly都不是终点。

## 7. 容量

保持 PROPOSED；不替换现有 ACTIVE 线。用户把本 workbench 交给本地 agent 后，agent按 [LOCAL_AGENT_PROMPT](../../workbench/latent-world-model-planning/LOCAL_AGENT_PROMPT.md) 自主推进小pilot与卡片内分支；状态变化仍由人决定。
